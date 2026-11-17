"""
Módulos ROS falsos (rclpy e mensagens) para testar o nó sem ROS.

Só o necessário para o ``line_vision_node``: ``Node`` com parâmetros,
publicadores que guardam as mensagens, assinaturas e timers registrados.
"""

import sys
import types


class _Msg:
    """Mensagem genérica: atributos com padrão e kwargs."""

    _fields = {}

    def __init__(self, **kw):
        for k, factory in self._fields.items():
            setattr(self, k, factory())
        for k, v in kw.items():
            setattr(self, k, v)


def msg(name, **fields):
    return type(name, (_Msg,), {'_fields': fields})


def install():
    """Registra os módulos falsos em ``sys.modules`` e devolve o rclpy falso."""
    Point2D = msg('Point2D', x=float, y=float)
    Pose2D = msg('Pose2D', position=Point2D, theta=float)
    BoundingBox2D = msg('BoundingBox2D', center=Pose2D, size_x=float, size_y=float)
    vm = types.ModuleType('vision_msgs.msg')
    vm.Point2D, vm.Pose2D, vm.BoundingBox2D = Point2D, Pose2D, BoundingBox2D

    Confidence = msg('Confidence', confidence=lambda: -1.0)
    attr = types.ModuleType('soccer_vision_attribute_msgs.msg')
    attr.Confidence = Confidence
    attr.Goalpost = msg('GoalpostAttr', side=int, team=int)
    attr.Robot = msg('RobotAttr', player_number=int, team=int, state=int, facing=int)

    Header = msg('Header', stamp=object, frame_id=str)
    std = types.ModuleType('std_msgs.msg')
    std.Header = Header

    sv = types.ModuleType('soccer_vision_2d_msgs.msg')
    sv.Ball = msg('Ball', bb=BoundingBox2D, center=Point2D, confidence=Confidence)
    sv.BallArray = msg('BallArray', header=Header, balls=list)
    sv.Goalpost = msg('Goalpost', bb=BoundingBox2D,
                      attributes=attr.Goalpost, confidence=Confidence)
    sv.GoalpostArray = msg('GoalpostArray', header=Header, posts=list)
    sv.Robot = msg('Robot', bb=BoundingBox2D, attributes=attr.Robot, confidence=Confidence)
    sv.RobotArray = msg('RobotArray', header=Header, robots=list)
    sv.MarkingIntersection = msg('MarkingIntersection', center=Point2D, num_rays=int, heading_rays=list,
                                 confidence=Confidence)
    sv.MarkingSegment = msg('MarkingSegment', start=Point2D, end=Point2D, confidence=Confidence)
    sv.MarkingEllipse = msg('MarkingEllipse', bb=BoundingBox2D,
                            center=Point2D, confidence=Confidence)
    sv.MarkingArray = msg('MarkingArray', header=Header, ellipses=list,
                          intersections=list, segments=list)
    sv.FieldBoundary = msg('FieldBoundary', header=Header, points=list, confidence=Confidence)

    sm = types.ModuleType('sensor_msgs.msg')
    sm.Image = msg('Image', header=Header, height=int, width=int, encoding=str, is_bigendian=int, step=int,
                   data=bytes)
    sm.CameraInfo = msg('CameraInfo', header=Header, k=lambda: [
                        0.0] * 9, d=list, width=int, height=int)

    ed = types.ModuleType('edrom_msgs.msg')
    ed.Landmark = msg('Landmark', id=int, distance_m=float, angle_rad=float)
    ed.LandmarkArray = msg('LandmarkArray', header=Header, landmarks=list)

    class _Param:
        def __init__(self, v):
            self.value = v

    class _Pub:
        def __init__(self, typ, topic):
            self.typ, self.topic, self.msgs = typ, topic, []

        def publish(self, m):
            self.msgs.append(m)

    class _Logger:
        def __init__(self):
            self.lines = []

        def info(self, s):
            self.lines.append(('info', s))

        def warn(self, s):
            self.lines.append(('warn', s))

        warning = warn

        def error(self, s):
            self.lines.append(('error', s))

    class Node:
        overrides = {}

        def __init__(self, name):
            self.name = name
            self.params = {}
            self.publishers = {}
            self.subscriptions = {}
            self.timers = []
            self._logger = _Logger()

        def declare_parameter(self, name, default):
            v = Node.overrides.get(name, default)
            self.params[name] = v
            return _Param(v)

        def create_publisher(self, typ, topic, qos):
            p = _Pub(typ, topic)
            self.publishers[topic] = p
            return p

        def create_subscription(self, typ, topic, cb, qos):
            self.subscriptions[topic] = (typ, cb)

        def create_timer(self, period, cb):
            self.timers.append((period, cb))

        def get_logger(self):
            return self._logger

        def destroy_node(self):
            pass

    rclpy = types.ModuleType('rclpy')
    rclpy.ok = lambda: True
    rclpy.init = lambda args=None: None
    rclpy.shutdown = lambda: None
    rclpy.spin = lambda node: None
    node_mod = types.ModuleType('rclpy.node')
    node_mod.Node = Node
    rclpy.node = node_mod

    mods = {
        'rclpy': rclpy, 'rclpy.node': node_mod,
        'vision_msgs': types.ModuleType('vision_msgs'), 'vision_msgs.msg': vm,
        'soccer_vision_attribute_msgs': types.ModuleType('soccer_vision_attribute_msgs'),
        'soccer_vision_attribute_msgs.msg': attr,
        'soccer_vision_2d_msgs': types.ModuleType('soccer_vision_2d_msgs'), 'soccer_vision_2d_msgs.msg': sv,
        'std_msgs': types.ModuleType('std_msgs'), 'std_msgs.msg': std,
        'sensor_msgs': types.ModuleType('sensor_msgs'), 'sensor_msgs.msg': sm,
        'edrom_msgs': types.ModuleType('edrom_msgs'), 'edrom_msgs.msg': ed,
    }
    for k, v in mods.items():
        sys.modules[k] = v
    for pkg in ('vision_msgs', 'soccer_vision_attribute_msgs', 'soccer_vision_2d_msgs', 'std_msgs',
                'sensor_msgs', 'edrom_msgs'):
        sys.modules[pkg].msg = sys.modules[pkg + '.msg']
    return rclpy, Node


def uninstall():
    """Remove os módulos falsos."""
    for k in list(sys.modules):
        fake = k.split('.')[0] in ('rclpy', 'vision_msgs', 'soccer_vision_attribute_msgs', 'soccer_vision_2d_msgs',
                                   'std_msgs', 'sensor_msgs', 'edrom_msgs')
        if fake or k == 'robocup_line_vision.ros.line_vision_node':
            del sys.modules[k]
