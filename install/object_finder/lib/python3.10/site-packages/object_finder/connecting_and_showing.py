#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

import cv2
from pathlib import Path
from ultralytics import YOLO

from object_finder import running_inference as ri

import soccer_vision_2d_msgs.msg as sv2dm 
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from ament_index_python.packages import get_package_share_directory


# Rotação (graus, sentido horário) -> código do cv2.rotate
ROTACOES = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}


def box_para_imagem_original(box, rotacao, w, h):
    """
    Converte uma caixa [cx, cy, bw, bh] detectada na imagem girada de volta
    para as coordenadas da imagem original da câmera (w x h), que é o que o
    camera_info e o TF descrevem — assim o IPM continua correto.
    """
    cx, cy, bw, bh = box
    if rotacao == 90:
        return [cy, h - cx, bh, bw]
    if rotacao == 180:
        return [w - cx, h - cy, bw, bh]
    if rotacao == 270:
        return [w - cy, cx, bh, bw]
    return [cx, cy, bw, bh]


class YoloSimulacao(Node):

    def __init__(self):
        super().__init__('vision')

        # Rotação aplicada à imagem antes do YOLO (câmera montada girada).
        # 0, 90, 180 ou 270 graus no sentido horário.
        self.rotacao = int(self.declare_parameter('image_rotation', 0).value) % 360
        if self.rotacao not in (0, *ROTACOES):
            self.get_logger().error(
                f'image_rotation={self.rotacao} inválido (use 0, 90, 180 ou 270); usando 0')
            self.rotacao = 0
        self.get_logger().info(f'Rotação da imagem: {self.rotacao} graus (horário)')

        self.bridge = CvBridge()
        model_path = (
            Path(get_package_share_directory("object_finder"))
            / "modelo"
            / "best.pt"
        )

        self.model = YOLO(str(model_path))

        # Subscriber da camera
        self.camera_subscriber = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback, 
            qos_profile_sensor_data, 
        )

        # Publisher IPM

        self.pub_ball = self.create_publisher(sv2dm.BallArray,'balls_in_image',1)
        self.pub_goal = self.create_publisher(sv2dm.GoalpostArray,'goal_posts_in_image',1)
        self.pub_robot = self.create_publisher(sv2dm.RobotArray,'robots_in_image',1)
        self.pub_inter = self.create_publisher(sv2dm.MarkingArray, 'markings_in_image',1)
        
    def image_callback(self, ros_image_msg):
        try:
            # Converte o frame para cv2
            frame = self.bridge.imgmsg_to_cv2(ros_image_msg,desired_encoding="bgr8")
            h, w = frame.shape[:2]

            # Desfaz a rotação física da câmera para o YOLO ver a imagem em pé
            if self.rotacao:
                frame = cv2.rotate(frame, ROTACOES[self.rotacao])

            # Roda o YOLO
            classes, scores, boxes, inference_frame = ri.detect_model(self.model, frame)

            # Caixas de volta para as coordenadas da imagem original (IPM)
            boxes = [box_para_imagem_original(b, self.rotacao, w, h) for b in boxes]

            # ROS Header
    
            header = ros_image_msg.header

            # Criação das mensagens vazias

            msg_ball = sv2dm.BallArray(header=header)
            msg_goal = sv2dm.GoalpostArray(header=header)
            msg_robot = sv2dm.RobotArray(header=header)
            msg_int = sv2dm.MarkingArray(header=header)

            # Loop das mensagens 
    
            for i in range(len(boxes)):
                box = boxes[i] # [x,y,w,h]
                cls = int(classes[i])
                conf = float(scores[i])

                # {0: 'ball', 1: 'goalpost', 2: 'robot', 3: 'L-Intersection', 4: 'T-Intersection', 5: 'X-Intersection', 6: 'crossbar'}

                # Bola 
                if cls == 0:
                    b = sv2dm.Ball()
                    b.center.x = float(box[0])
                    b.center.y = float(box[1])
                    b.confidence.confidence = conf
                    msg_ball.balls.append(b)

                if cls == 1:
                    g = sv2dm.Goalpost()
                    g.bb.center.position.x = float(box[0])
                    g.bb.center.position.y = float(box[1])
                    g.bb.size_x = float(box[2])
                    g.bb.size_y = float(box[3])
                    g.confidence.confidence = conf 
                    msg_goal.posts.append(g)

                if cls == 2:
                    r = sv2dm.Robot()
                    r.bb.center.position.x = float(box[0])
                    r.bb.center.position.y = float(box[1])
                    r.bb.size_x = float(box[2])
                    r.bb.size_y = float(box[3])
                    r.confidence.confidence = conf 
                    msg_robot.robots.append(r)


                if cls == 3 or cls == 4 or cls == 5:
                    intersecao = sv2dm.MarkingIntersection()  
                    intersecao.center.x = float(box[0])
                    intersecao.center.y = float(box[1])  
                    intersecao.confidence.confidence = conf 
                    if cls == 3: # L
                        intersecao.num_rays = 2
                    elif cls == 4: # T
                        intersecao.num_rays = 3
                    elif cls == 5: # X
                        intersecao.num_rays = 4
                    
                    intersecao.heading_rays = [] # vazio de acordo com a informação da mensagem
                    msg_int.intersections.append(intersecao)

            # visualização?

            cv2.imshow('inference_frame',inference_frame)
            cv2.waitKey(1)

            # publicação

            self.pub_ball.publish(msg_ball)
            self.pub_goal.publish(msg_goal)
            self.pub_robot.publish(msg_robot)
            self.pub_inter.publish(msg_int)

        except Exception as e:
            self.get_logger().error(f'Erro: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = YoloSimulacao()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
