"""Pose da câmera em relação ao chão, por dois caminhos.

Referenciais (todos com x para frente, y para a esquerda, z para cima):
  base_footprint  no chão, logo abaixo do robô, com o yaw do torso. É nele que o IPM devolve os pontos.
  câmera          olhando ao longo de +x.

Modos:
  fixed       sem URDF. O eixo do tilt fica a uma altura fixa do chão; o corpo tem uma inclinação fixa; a
              cabeça gira pan e depois tilt (eixos supostos concorrentes); a lente fica a `camera_offset` do
              eixo do tilt. Tudo medido no robô.
  kinematics  cadeia completa pelo URDF do robô: sola do pé de apoio -> perna -> torso -> pescoço -> link da
              câmera, com todos os ângulos de junta. A altura e a inclinação do torso saem das pernas,
              supondo o pé de apoio plano no chão.
"""
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import numpy as np


def translation(xyz):
    t = np.eye(4)
    t[:3, 3] = xyz
    return t


def rotation(r3):
    t = np.eye(4)
    t[:3, :3] = r3
    return t


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def axis_angle(axis, angle):
    """Matriz de rotação de `angle` em torno de `axis` (Rodrigues)."""
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    k = np.array([[0.0, -axis[2], axis[1]], [axis[2], 0.0, -axis[0]], [-axis[1], axis[0], 0.0]])
    return np.eye(3) + math.sin(angle) * k + (1.0 - math.cos(angle)) * (k @ k)


def invert(t):
    inv = np.eye(4)
    inv[:3, :3] = t[:3, :3].T
    inv[:3, 3] = -t[:3, :3].T @ t[:3, 3]
    return inv


@dataclass
class CameraPose:
    footprint_camera: np.ndarray            # 4x4, base_footprint -> câmera
    footprint_torso: np.ndarray = None      # 4x4, base_footprint -> torso (só no modo kinematics)
    support: str = ''                       # pé de apoio no modo kinematics

    @property
    def height(self):
        return float(self.footprint_camera[2, 3])

    @property
    def pitch(self):
        """Inclinação do eixo óptico para baixo, em rad (positivo olhando para o chão)."""
        forward = self.footprint_camera[:3, 0]
        return math.atan2(-forward[2], math.hypot(forward[0], forward[1]))


def fixed_pose(tilt_axis_height, body_pitch, pan, tilt, camera_offset):
    """Modo fixed: eixo do tilt a `tilt_axis_height` m do chão, corpo inclinado `body_pitch` rad para frente.

    pan positivo olha para a esquerda; tilt positivo olha para baixo. `camera_offset` = eixo do tilt -> lente,
    [x frente, y esquerda, z cima] com a cabeça em pan = tilt = 0.
    """
    t = (translation((0.0, 0.0, tilt_axis_height)) @ rotation(rot_y(body_pitch)) @ rotation(rot_z(pan))
         @ rotation(rot_y(tilt)) @ translation(camera_offset))
    return CameraPose(t)


@dataclass
class Joint:
    name: str
    type: str
    parent: str
    child: str
    origin: np.ndarray      # 4x4, pai -> junta em zero
    axis: np.ndarray

    def transform(self, q):
        if self.type in ('revolute', 'continuous'):
            return self.origin @ rotation(axis_angle(self.axis, q))
        if self.type == 'prismatic':
            return self.origin @ translation(self.axis * q)
        return self.origin


class RobotModel:
    """Cinemática direta a partir do URDF (só origens e eixos das juntas)."""

    def __init__(self, urdf_path):
        root = ET.parse(urdf_path).getroot()
        self.links = {link.get('name') for link in root.findall('link')}
        self.joint_by_child = {}
        for j in root.findall('joint'):
            origin = j.find('origin')
            xyz = [float(v) for v in (origin.get('xyz', '0 0 0') if origin is not None else '0 0 0').split()]
            rpy = [float(v) for v in (origin.get('rpy', '0 0 0') if origin is not None else '0 0 0').split()]
            axis = j.find('axis')
            joint = Joint(
                name=j.get('name'), type=j.get('type'),
                parent=j.find('parent').get('link'), child=j.find('child').get('link'),
                origin=translation(xyz) @ rotation(rot_z(rpy[2]) @ rot_y(rpy[1]) @ rot_x(rpy[0])),
                axis=np.array([float(v) for v in (axis.get('xyz') if axis is not None else '1 0 0').split()]),
            )
            self.joint_by_child[joint.child] = joint

    def chain(self, root, tip):
        joints = []
        link = tip
        while link != root:
            if link not in self.joint_by_child:
                raise KeyError(f'o link {tip} não descende de {root} no URDF')
            joint = self.joint_by_child[link]
            joints.append(joint)
            link = joint.parent
        return joints[::-1]

    def transform(self, root, tip, positions):
        """Transformação 4x4 de `root` para `tip`. Juntas ausentes em `positions` ficam em zero."""
        t = np.eye(4)
        for joint in self.chain(root, tip):
            t = t @ joint.transform(positions.get(joint.name, 0.0))
        return t


class CameraKinematics:
    """Modo kinematics: pose da câmera pelo URDF e pelos ângulos de todas as juntas."""

    def __init__(self, model, torso_link, camera_link, foot_links, camera_offset=(0.0, 0.0, 0.0),
                 sole_offset=None):
        self.model = model
        self.torso_link = torso_link
        self.camera_link = camera_link
        self.foot_links = dict(foot_links)
        missing = [n for n in (torso_link, camera_link, *self.foot_links.values()) if n not in model.links]
        if missing:
            raise ValueError(f'links {missing} não existem no URDF; links disponíveis: {sorted(model.links)}')
        for tip in (camera_link, *self.foot_links.values()):
            model.chain(torso_link, tip)        # falha cedo se a cadeia não existe
        self.camera_offset = translation(camera_offset)
        sole_offset = sole_offset or {}
        self.sole_offset = {side: translation(sole_offset.get(side, (0.0, 0.0, 0.0))) for side in self.foot_links}
        self.support = 'left'

    def torso_camera(self, positions):
        return self.model.transform(self.torso_link, self.camera_link, positions) @ self.camera_offset

    def torso_sole(self, side, positions):
        return self.model.transform(self.torso_link, self.foot_links[side], positions) @ self.sole_offset[side]

    def choose_support(self, soles, mode='auto', hysteresis=0.005):
        """Pé de apoio = sola mais baixa no eixo z do torso; troca só se a outra ficar `hysteresis` m abaixo."""
        if mode in ('left', 'right'):
            return mode
        other = 'right' if self.support == 'left' else 'left'
        if soles[other][2, 3] < soles[self.support][2, 3] - hysteresis:
            self.support = other
        return self.support

    def pose(self, positions, support='auto'):
        soles = {side: self.torso_sole(side, positions) for side in ('left', 'right')}
        side = self.choose_support(soles, support)
        # A sola de apoio está plana no chão: no referencial dela o chão é z = 0.
        sole_torso = invert(soles[side])
        position = sole_torso[:3, 3]
        heading = sole_torso[:3, 0]
        yaw = math.atan2(heading[1], heading[0])
        sole_footprint = translation((position[0], position[1], 0.0)) @ rotation(rot_z(yaw))
        footprint_torso = invert(sole_footprint) @ sole_torso
        return CameraPose(footprint_torso @ self.torso_camera(positions), footprint_torso, side)
