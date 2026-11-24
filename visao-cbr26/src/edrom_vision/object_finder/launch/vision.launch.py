# vision.launch.py
# usb_cam -> YOEO-26n (OpenVINO): detecções em soccer_vision_2d_msgs e máscara em /vision/segmentation.
#
#   ros2 launch object_finder vision.launch.py                      # robô real, CPU
#   ros2 launch object_finder vision.launch.py device:=GPU          # iGPU
#   ros2 launch object_finder vision.launch.py sim_mode:=True       # Webots (/camera/image, sem usb_cam)

import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    arg = LaunchConfiguration

    # Configuração da câmera (mesmo arquivo usado pelo camera_calibrator)
    usb_cam_params = os.path.join(get_package_share_directory("object_finder"), "config", "usb_cam.yaml")
    with open(usb_cam_params) as f:
        usb_cam_cfg = next(iter(yaml.safe_load(f).values()))["ros__parameters"]

    yoeo_params = {
        "use_sim_time": arg("sim_mode"),
        "model_path": arg("model_path"),
        "device": arg("device"),
        "threads": arg("threads"),
        "img_output": arg("img_output"),
        "debug_image": arg("debug_image"),
        "undistort": arg("undistort"),
        "conf_ball": arg("conf_ball"),
        "conf_goalpost": arg("conf_goalpost"),
        "conf_robot": arg("conf_robot"),
        "conf_intersection": arg("conf_intersection"),
    }

    return LaunchDescription([

        DeclareLaunchArgument("video_device", default_value=usb_cam_cfg["video_device"],
                              description="Dispositivo da câmera USB"),
        DeclareLaunchArgument("camera_name", default_value=usb_cam_cfg["camera_name"],
                              description="Câmera usada: escolhe o arquivo de calibração em config/"),
        DeclareLaunchArgument("camera_info_url",
                              default_value=["package://object_finder/config/", arg("camera_name"),
                                             "_camera-info.yaml"],
                              description="URL do YAML de calibração intrínseca da câmera"),
        DeclareLaunchArgument("sim_mode", default_value="False",
                              description="Webots: lê /camera/image e não sobe o usb_cam"),
        DeclareLaunchArgument("model_path", default_value="", description="vazio = modelo instalado no pacote"),
        DeclareLaunchArgument("device", default_value="CPU", description="CPU ou GPU (iGPU)"),
        DeclareLaunchArgument("threads", default_value="0", description="threads na CPU; 0 = automático"),
        DeclareLaunchArgument("img_output", default_value="False", description="janela com caixas e máscara"),
        DeclareLaunchArgument("debug_image", default_value="False", description="publica vision_debug"),
        DeclareLaunchArgument("undistort", default_value="True",
                              description="tira a distorção da imagem com o camera_info antes da rede"),
        DeclareLaunchArgument("conf_ball", default_value="0.45"),
        DeclareLaunchArgument("conf_goalpost", default_value="0.45"),
        DeclareLaunchArgument("conf_robot", default_value="0.45"),
        DeclareLaunchArgument("conf_intersection", default_value="0.45"),

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
    ])
