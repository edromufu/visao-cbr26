"""
vision_messages.py

Converte detecções validadas e resultados da segmentação nas mensagens
`soccer_vision_2d_msgs` que o `soccer_ipm` consome (pixels -> metros).

Atenção: o rclpy exige `float` nos campos `double`/`float`; um `int` levanta
AssertionError. Por isso todo valor numérico passa por `float()`.
"""

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

import soccer_vision_2d_msgs.msg as sv2dm
from std_msgs.msg import Header
from vision_msgs.msg import BoundingBox2D, Point2D

from .detections import Detection, YoloClass
from object_finder.pipeline import Obstacle

# Número de raios (linhas que saem do ponto) de cada tipo de interseção.
INTERSECTION_NUM_RAYS = {
    YoloClass.L_INTERSECTION: 2,
    YoloClass.T_INTERSECTION: 3,
    YoloClass.X_INTERSECTION: 4,
}


@dataclass(frozen=True)
class DetectionMessages:
    """Uma mensagem de array por tópico `*_in_image` do soccer_ipm."""
    balls: sv2dm.BallArray
    goalposts: sv2dm.GoalpostArray
    robots: sv2dm.RobotArray
    markings: sv2dm.MarkingArray


def build_detection_messages(header: Header, detections: Iterable[Detection]) -> DetectionMessages:
    """Monta as mensagens a partir das detecções JÁ validadas."""
    messages = DetectionMessages(
        balls=sv2dm.BallArray(header=header),
        goalposts=sv2dm.GoalpostArray(header=header),
        robots=sv2dm.RobotArray(header=header),
        markings=sv2dm.MarkingArray(header=header),
    )
    for detection in detections:
        yolo_class = detection.yolo_class
        if yolo_class == YoloClass.BALL:
            messages.balls.balls.append(_ball(detection))
        elif yolo_class == YoloClass.GOALPOST:
            messages.goalposts.posts.append(_goalpost(detection))
        elif yolo_class == YoloClass.ROBOT:
            messages.robots.robots.append(_robot(detection))
        elif yolo_class in INTERSECTION_NUM_RAYS:
            messages.markings.intersections.append(_intersection(detection))
    return messages


def build_field_boundary_message(
    header: Header,
    points: Sequence[Tuple[int, int]],
) -> Optional[sv2dm.FieldBoundary]:
    """Fronteira do campo em pixels, ou None se não há pontos.

    Uma fronteira vazia derruba o `soccer_ipm` (acessa `points.shape[1]`),
    então quem chama deve pular a publicação quando receber None.
    """
    if not points:
        return None
    message = sv2dm.FieldBoundary(header=header)
    message.points = [Point2D(x=float(x), y=float(y)) for x, y in points]
    return message


def build_obstacle_array_message(
    header: Header,
    obstacles: Iterable[Obstacle],
) -> sv2dm.ObstacleArray:
    """Obstáculos da segmentação (lista vazia é uma mensagem válida)."""
    message = sv2dm.ObstacleArray(header=header)
    for obstacle in obstacles:
        item = sv2dm.Obstacle()
        item.bb.center.position.x = float(obstacle.x + obstacle.width / 2.0)
        item.bb.center.position.y = float(obstacle.y + obstacle.height / 2.0)
        item.bb.size_x = float(obstacle.width)
        item.bb.size_y = float(obstacle.height)
        message.obstacles.append(item)
    return message


# ----------------------------------------------------------------------
# Itens individuais
# ----------------------------------------------------------------------

def _fill_bounding_box(bounding_box: BoundingBox2D, detection: Detection) -> None:
    bounding_box.center.position.x = float(detection.center_x)
    bounding_box.center.position.y = float(detection.center_y)
    bounding_box.size_x = float(detection.width)
    bounding_box.size_y = float(detection.height)


def _ball(detection: Detection) -> sv2dm.Ball:
    ball = sv2dm.Ball()
    _fill_bounding_box(ball.bb, detection)
    ball.center.x = float(detection.center_x)  # o IPM projeta o centro da bola
    ball.center.y = float(detection.center_y)
    ball.confidence.confidence = float(detection.confidence)
    return ball


def _goalpost(detection: Detection) -> sv2dm.Goalpost:
    post = sv2dm.Goalpost()
    _fill_bounding_box(post.bb, detection)
    post.confidence.confidence = float(detection.confidence)
    return post


def _robot(detection: Detection) -> sv2dm.Robot:
    robot = sv2dm.Robot()
    _fill_bounding_box(robot.bb, detection)
    robot.confidence.confidence = float(detection.confidence)
    return robot


def _intersection(detection: Detection) -> sv2dm.MarkingIntersection:
    intersection = sv2dm.MarkingIntersection()
    intersection.center.x = float(detection.center_x)
    intersection.center.y = float(detection.center_y)
    intersection.num_rays = INTERSECTION_NUM_RAYS[detection.yolo_class]
    intersection.heading_rays = []  # o modelo não estima a direção dos raios
    intersection.confidence.confidence = float(detection.confidence)
    return intersection


# ----------------------------------------------------------------------
# Câmera de cabeça para baixo
# ----------------------------------------------------------------------

def rotate_message_180(message, width: float, height: float):
    """Leva os pixels de uma mensagem `*_in_image` da imagem girada 180 graus para a original.

    O nó processa a imagem em pé (girada), mas publica nas coordenadas da imagem
    original da câmera, que é o referencial do camera_info usado pelo soccer_ipm.
    Girar 180 graus: x -> width - x, y -> height - y; os tamanhos não mudam.
    """
    def point(p):
        p.x, p.y = float(width - p.x), float(height - p.y)

    def box(b):
        point(b.center.position)

    if isinstance(message, sv2dm.BallArray):
        for ball in message.balls:
            point(ball.center)
            box(ball.bb)
    elif isinstance(message, sv2dm.GoalpostArray):
        for post in message.posts:
            box(post.bb)
    elif isinstance(message, sv2dm.RobotArray):
        for robot in message.robots:
            box(robot.bb)
    elif isinstance(message, sv2dm.MarkingArray):
        for intersection in message.intersections:
            point(intersection.center)
    elif isinstance(message, sv2dm.FieldBoundary):
        for p in message.points:
            point(p)
        message.points = list(message.points)[::-1]   # mantém a ordem da esquerda para a direita
    elif isinstance(message, sv2dm.ObstacleArray):
        for obstacle in message.obstacles:
            box(obstacle.bb)
    return message
