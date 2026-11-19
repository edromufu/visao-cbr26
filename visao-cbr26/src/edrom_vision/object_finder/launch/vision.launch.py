# vision.launch.py (Versão Unificada)
#
# Robô real (usb_cam):   ros2 launch object_finder vision.launch.py
# Simulação (Webots):    ros2 launch object_finder vision.launch.py simulacao:=true
# Outras opções:         show_window:=false  model_file:=/caminho/yolo26n_best.pt
#                        publish_tf:=true cam_z:=0.5 cam_pitch:=0.3  (só se o robô não publica a TF da câmera)

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition, UnlessCondition
from ament_index_python.packages import get_package_share_directory
import os
import yaml

# Tópicos da câmera do robô AUREA no Webots
SIM_IMAGE_TOPIC = "/AUREA/camera_optical_frame/image_color"


def generate_launch_description():

    config_dir = os.path.join(get_package_share_directory("object_finder"), "config")

    # Configuração da câmera (mesmo arquivo usado pelo camera_calibrator)
    usb_cam_params = os.path.join(config_dir, "usb_cam.yaml")
    with open(usb_cam_params) as f:
        usb_cam_cfg = next(iter(yaml.safe_load(f).values()))["ros__parameters"]

    # Parâmetros do nó de visão (segmentação, validação, HSV)
    vision_params = os.path.join(config_dir, "vision_params.yaml")

    simulacao = LaunchConfiguration("simulacao")

    return LaunchDescription([

        DeclareLaunchArgument(
            "video_device",
            default_value=usb_cam_cfg["video_device"],
            description="Dispositivo da câmera USB",
        ),

        DeclareLaunchArgument(
            "camera_name",
            default_value=usb_cam_cfg["camera_name"],
            description="Câmera usada (verri ou milare): escolhe o arquivo de calibração",
        ),

        DeclareLaunchArgument(
            "camera_info_url",
            default_value=[
                "package://object_finder/config/",
                LaunchConfiguration("camera_name"),
                "_camera-info.yaml",
            ],
            description="URL do YAML de calibração intrínseca da câmera",
        ),

        DeclareLaunchArgument("simulacao", default_value="false",
                              description="true = câmera do Webots (AUREA) em vez do usb_cam"),
        DeclareLaunchArgument("show_window", default_value="true",
                              description="Abre a janela do OpenCV com a imagem de debug"),
        DeclareLaunchArgument("model_file", default_value="best.pt",
                              description="Pesos em modelo/ (ex.: best.pt, yolo26n_best.pt) ou caminho absoluto"),
        DeclareLaunchArgument("output_frame", default_value="base_footprint",
                              description="Frame do corpo do robô (pai da TF da câmera)"),
        DeclareLaunchArgument("camera_frame", default_value=usb_cam_cfg["frame_id"]),

        # TF da câmera: só se o robô NÃO publica output_frame -> camera_optical_frame.
        DeclareLaunchArgument("publish_tf", default_value="false"),
        DeclareLaunchArgument("cam_x", default_value="0.0"),      # m (x à frente)
        DeclareLaunchArgument("cam_y", default_value="0.0"),      # m (y à esquerda)
        DeclareLaunchArgument("cam_z", default_value="0.5"),      # m (z para cima)
        DeclareLaunchArgument("cam_roll", default_value="0.0"),   # rad
        DeclareLaunchArgument("cam_pitch", default_value="0.0"),  # rad (positivo = olha para baixo)
        DeclareLaunchArgument("cam_yaw", default_value="0.0"),    # rad

        Node(
            package="usb_cam",
            executable="usb_cam_node_exe",
            name="usb_cam",
            namespace="camera",
            output="screen",
            condition=UnlessCondition(simulacao),
            # usb_cam.yaml primeiro; o dict abaixo sobrescreve com os argumentos do launch
            parameters=[usb_cam_params, {
                "use_sim_time": False,
                "camera_name": LaunchConfiguration("camera_name"),
                "video_device": LaunchConfiguration("video_device"),
                "camera_info_url": LaunchConfiguration("camera_info_url"),
            }],
        ),

        # output_frame -> camera_link (pose da câmera) -> camera_optical_frame
        # (convenção óptica: z à frente, x à direita, y para baixo).
        Node(
            package="tf2_ros", executable="static_transform_publisher", name="camera_tf_body",
            condition=IfCondition(LaunchConfiguration("publish_tf")),
            arguments=["--x", LaunchConfiguration("cam_x"), "--y", LaunchConfiguration("cam_y"),
                       "--z", LaunchConfiguration("cam_z"), "--roll", LaunchConfiguration("cam_roll"),
                       "--pitch", LaunchConfiguration("cam_pitch"), "--yaw", LaunchConfiguration("cam_yaw"),
                       "--frame-id", LaunchConfiguration("output_frame"), "--child-frame-id", "camera_link"],
        ),
        Node(
            package="tf2_ros", executable="static_transform_publisher", name="camera_tf_optical",
            condition=IfCondition(LaunchConfiguration("publish_tf")),
            arguments=["--roll", "-1.5707963", "--pitch", "0", "--yaw", "-1.5707963",
                       "--frame-id", "camera_link", "--child-frame-id", LaunchConfiguration("camera_frame")],
        ),

        Node(
            package='object_finder',
            executable='finder',
            name='vision',
            output='screen',
            emulate_tty=True,
            parameters=[vision_params, {
                "use_sim_time": ParameterValue(simulacao, value_type=bool),
                "show_window": ParameterValue(LaunchConfiguration("show_window"), value_type=bool),
                "model_file": ParameterValue(LaunchConfiguration("model_file"), value_type=str),
            }],
            remappings=[
                ("/camera/image_raw", PythonExpression([
                    "'", SIM_IMAGE_TOPIC, "' if '", simulacao, "'.lower() == 'true' else '/camera/image_raw'"
                ])),
            ],
        ),
    ])
