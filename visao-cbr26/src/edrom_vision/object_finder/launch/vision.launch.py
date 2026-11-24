# vision.launch.py
# usb_cam -> YOEO-26n (OpenVINO) -> IPM. Detecções em soccer_vision_2d_msgs, posições no chão em soccer_vision_3d_msgs.
#
# Pose da câmera no IPM (pose_source):
#   fixed       medidas do robô: altura do eixo do tilt, inclinação do corpo, offset da lente; pan/tilt de
#               /joint_states ou fixos. Meça tudo no robô, na pose de caminhada.
#   kinematics  URDF do robô + todas as juntas de /joint_states (sola do pé de apoio -> perna -> torso -> câmera).
#
#   ros2 launch object_finder vision.launch.py tilt_axis_height:=0.49 "camera_offset:=[0.05, 0.0, 0.02]"
#   ros2 launch object_finder vision.launch.py use_joint_states:=False tilt:=0.52
#   ros2 launch object_finder vision.launch.py pose_source:=kinematics urdf_path:=/caminho/robo.urdf \
#       camera_link:=head_tilt_link left_foot_link:=l_ank_roll_link right_foot_link:=r_ank_roll_link rviz:=True

import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arg = LaunchConfiguration
    share = get_package_share_directory("object_finder")

    # Configuração da câmera (mesmo arquivo usado pelo camera_calibrator)
    usb_cam_params = os.path.join(share, "config", "usb_cam.yaml")
    with open(usb_cam_params) as f:
        usb_cam_cfg = next(iter(yaml.safe_load(f).values()))["ros__parameters"]

    yoeo_params = {
        "use_sim_time": arg("sim_mode"),
        "model_path": arg("model_path"),
        "device": arg("device"),
        "threads": arg("threads"),
        "img_output": arg("img_output"),
        "debug_image": arg("debug_image"),
        # O IPM tira a distorção dos pixels detectados com o camera_info: a imagem vai crua para a rede.
        "undistort": False,
        "conf_ball": arg("conf_ball"),
        "conf_goalpost": arg("conf_goalpost"),
        "conf_robot": arg("conf_robot"),
        "conf_intersection": arg("conf_intersection"),
    }

    return LaunchDescription([

        # ---------------- câmera ----------------
        DeclareLaunchArgument("video_device", default_value=usb_cam_cfg["video_device"],
                              description="Dispositivo da câmera USB"),
        DeclareLaunchArgument("camera_name", default_value=usb_cam_cfg["camera_name"],
                              description="Câmera usada: escolhe o arquivo de calibração em config/"),
        DeclareLaunchArgument("camera_info_url",
                              default_value=["package://object_finder/config/", arg("camera_name"),
                                             "_camera-info.yaml"],
                              description="URL do YAML de calibração intrínseca (sem K = IPM usa o fov)"),
        DeclareLaunchArgument("sim_mode", default_value="False",
                              description="Webots: lê /camera/image e não sobe o usb_cam"),
        # ---------------- YOEO ----------------
        DeclareLaunchArgument("model_path", default_value="", description="vazio = modelo instalado no pacote"),
        DeclareLaunchArgument("device", default_value="CPU", description="CPU ou GPU (iGPU)"),
        DeclareLaunchArgument("threads", default_value="0", description="threads na CPU; 0 = automático"),
        DeclareLaunchArgument("img_output", default_value="True", description="janela com as detecções do YOEO"),
        DeclareLaunchArgument("debug_image", default_value="False", description="publica vision_debug"),
        DeclareLaunchArgument("conf_ball", default_value="0.45"),
        DeclareLaunchArgument("conf_goalpost", default_value="0.45"),
        DeclareLaunchArgument("conf_robot", default_value="0.45"),
        DeclareLaunchArgument("conf_intersection", default_value="0.45"),
        # ---------------- IPM ----------------
        DeclareLaunchArgument("pose_source", default_value="fixed", description="fixed ou kinematics"),
        DeclareLaunchArgument("camera_offset", default_value="[0.0, 0.0, 0.0]",
                              description="eixo do tilt (fixed) ou camera_link (kinematics) -> lente "
                                          "[x frente, y esquerda, z cima], m"),
        DeclareLaunchArgument("fov", default_value="1.6", description="FOV horizontal, rad (sem calibração)"),
        DeclareLaunchArgument("show", default_value="True", description="janela com a vista de cima"),
        # modo fixed
        DeclareLaunchArgument("tilt_axis_height", default_value="0.49",
                              description="altura do eixo do tilt (servo da cabeça) ao chão, m — MEÇA no robô"),
        DeclareLaunchArgument("body_pitch", default_value="0.0",
                              description="inclinação do corpo para frente, rad (corrige também o zero do tilt)"),
        DeclareLaunchArgument("use_joint_states", default_value="True", description="pan/tilt de /joint_states"),
        DeclareLaunchArgument("pan_joint", default_value="head_pan", description="nome da junta de pan"),
        DeclareLaunchArgument("tilt_joint", default_value="head_tilt", description="nome da junta de tilt"),
        DeclareLaunchArgument("pan", default_value="0.0", description="pan fixo, rad (sem /joint_states)"),
        DeclareLaunchArgument("tilt", default_value="0.0", description="tilt fixo, rad, positivo para baixo"),
        # modo kinematics
        DeclareLaunchArgument("urdf_path", default_value="",
                              description="URDF do robô (juntas com os mesmos nomes de /joint_states)"),
        DeclareLaunchArgument("torso_link", default_value="base_link", description="link do torso no URDF"),
        DeclareLaunchArgument("camera_link", default_value="", description="link em que a câmera está presa"),
        DeclareLaunchArgument("left_foot_link", default_value="", description="último link da perna esquerda"),
        DeclareLaunchArgument("right_foot_link", default_value="", description="último link da perna direita"),
        DeclareLaunchArgument("sole_offset_left", default_value="[0.0, 0.0, 0.0]",
                              description="link do pé esquerdo -> centro da sola, m"),
        DeclareLaunchArgument("sole_offset_right", default_value="[0.0, 0.0, 0.0]",
                              description="link do pé direito -> centro da sola, m"),
        DeclareLaunchArgument("support_foot", default_value="auto", description="auto, left ou right"),
        DeclareLaunchArgument("rviz", default_value="False",
                              description="robot_state_publisher + RViz (modo kinematics)"),

        Node(
            package="usb_cam",
            executable="usb_cam_node_exe",
            name="usb_cam",
            namespace="camera",
            output="screen",
            # usb_cam.yaml primeiro; o dict abaixo sobrescreve com os argumentos do launch
            parameters=[usb_cam_params, {
                "use_sim_time": False,
                "camera_name": arg("camera_name"),
                "video_device": arg("video_device"),
                "camera_info_url": arg("camera_info_url"),
            }],
            condition=UnlessCondition(arg("sim_mode")),
        ),

        Node(
            package="object_finder",
            executable="finder",
            name="vision",
            output="screen",
            parameters=[yoeo_params],
            condition=UnlessCondition(arg("sim_mode")),
        ),

        Node(
            package="object_finder",
            executable="finder",
            name="vision",
            output="screen",
            parameters=[yoeo_params],
            remappings=[("/camera/image_raw", "/camera/image")],
            condition=IfCondition(arg("sim_mode")),
        ),

        Node(
            package="object_finder",
            executable="ipm",
            name="yoeo_ipm",
            output="screen",
            parameters=[{
                "use_sim_time": arg("sim_mode"),
                "pose_source": arg("pose_source"),
                "output_frame": "base_footprint",
                "camera.offset": arg("camera_offset"),
                "camera.fov": arg("fov"),
                "camera.width": usb_cam_cfg["image_width"],
                "camera.height": usb_cam_cfg["image_height"],
                "debug.show": arg("show"),
                "fixed.tilt_axis_height": arg("tilt_axis_height"),
                "fixed.body_pitch": arg("body_pitch"),
                "head.from_joint_states": arg("use_joint_states"),
                "head.pan_joint": arg("pan_joint"),
                "head.tilt_joint": arg("tilt_joint"),
                "head.pan": arg("pan"),
                "head.tilt": arg("tilt"),
                "urdf_path": arg("urdf_path"),
                "kinematics.torso_link": arg("torso_link"),
                "kinematics.camera_link": arg("camera_link"),
                "kinematics.left_foot_link": arg("left_foot_link"),
                "kinematics.right_foot_link": arg("right_foot_link"),
                "kinematics.sole_offset_left": arg("sole_offset_left"),
                "kinematics.sole_offset_right": arg("sole_offset_right"),
                "kinematics.support_foot": arg("support_foot"),
                "goalposts.footpoint_out_of_image_threshold": 0.8,
                "robots.footpoint_out_of_image_threshold": 0.8,
            }],
            remappings=[
                ("camera_info", "/camera/camera_info"),
            ],
        ),

        # Visualização: o IPM publica base_footprint -> torso_link; o robot_state_publisher, as pernas e a cabeça
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": ParameterValue(Command(["cat ", arg("urdf_path")]), value_type=str)}],
            condition=IfCondition(arg("rviz")),
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", os.path.join(share, "rviz", "ipm.rviz")],
            condition=IfCondition(arg("rviz")),
        ),
    ])
