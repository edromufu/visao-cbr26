# vision.launch.py (Versão Unificada)
#
# Robô real (usb_cam):     ros2 launch object_finder vision.launch.py
# Simulação (Webots/AUREA): ros2 launch object_finder vision.launch.py start_camera:=False use_sim_time:=True \
#     image_topic:=/AUREA/camera_optical_frame/image_color \
#     camera_info_topic:=/AUREA/camera_optical_frame/camera_info [start_webots:=True]

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import yaml


def _has_pkg(name):
    try:
        get_package_share_directory(name)
        return True
    except Exception:  # noqa: BLE001
        return False


def generate_launch_description():

    share = get_package_share_directory('object_finder')

    # Configuração da câmera (mesmo arquivo usado pelo camera_calibrator)
    usb_cam_params = os.path.join(share, 'config', 'usb_cam.yaml')
    with open(usb_cam_params) as f:
        usb_cam_cfg = next(iter(yaml.safe_load(f).values()))['ros__parameters']

    LC = LaunchConfiguration
    sim_time = ParameterValue(LC('use_sim_time'), value_type=bool)

    args = [
        DeclareLaunchArgument(
            'video_device',
            default_value=usb_cam_cfg['video_device'],
            description='Dispositivo da câmera USB',
        ),

        DeclareLaunchArgument(
            'camera_name',
            default_value=usb_cam_cfg['camera_name'],
            description='Câmera usada (verri ou milare): escolhe o arquivo de calibração',
        ),

        DeclareLaunchArgument(
            'camera_info_url',
            default_value=[
                'package://object_finder/config/',
                LC('camera_name'),
                '_camera-info.yaml',
            ],
            description='URL do YAML de calibração intrínseca da câmera',
        ),

        # Câmera / simulação
        DeclareLaunchArgument('start_camera', default_value='True',
                              description='Sobe o usb_cam (False na simulação)'),
        DeclareLaunchArgument('start_webots', default_value='False',
                              description='Sobe o Webots + driver do AUREA (my_package/robot_launch.py)'),
        DeclareLaunchArgument('use_sim_time', default_value='False'),
        DeclareLaunchArgument('image_topic', default_value='/camera/image_raw'),
        DeclareLaunchArgument('camera_info_topic', default_value='/camera/camera_info'),

        # Visão (estrutura de linhas + YOLO)
        DeclareLaunchArgument('calib_dir', default_value=os.path.join(share, 'calib', 'padrao_webots'),
                              description='Pasta com green_pixels.csv e white_pixels.csv (calibração de cor)'),
        DeclareLaunchArgument('model_path', default_value=os.path.join(share, 'modelo', 'best.pt'),
                              description='Modelo YOLO (.pt ou .onnx)'),
        DeclareLaunchArgument('use_yolo', default_value='True'),
        DeclareLaunchArgument('img_output', default_value='True',
                              description='Janela OpenCV com o overlay'),
        DeclareLaunchArgument('publish_debug_image', default_value='True',
                              description='Overlay em processed_image_topic'),
        DeclareLaunchArgument('processing_fps', default_value='0.0',
                              description='Taxa máxima de processamento (0 = todos os frames)'),
        DeclareLaunchArgument('params_file', default_value=os.path.join(share, 'config', 'params.yaml'),
                              description='Limiares do pipeline'),

        # Projeção ao chão própria (o IPM fica para depois)
        DeclareLaunchArgument('publish_projection', default_value='False',
                              description='Publica line_vision/markings_relative (soccer_vision_3d_msgs)'),
        DeclareLaunchArgument('camera_altura_m', default_value='0.70'),
        DeclareLaunchArgument('camera_pitch_rad', default_value='0.0'),
    ]

    camera = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        namespace='camera',
        output='screen',
        condition=IfCondition(LC('start_camera')),
        # usb_cam.yaml primeiro; o dict abaixo sobrescreve com os argumentos do launch
        parameters=[usb_cam_params, {
            'use_sim_time': sim_time,
            'camera_name': LC('camera_name'),
            'video_device': LC('video_device'),
            'camera_info_url': LC('camera_info_url'),
        }],
    )

    vision = Node(
        package='object_finder',
        executable='finder',
        name='vision',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'use_sim_time': sim_time,
            'image_topic': LC('image_topic'),
            'camera_info_topic': LC('camera_info_topic'),
            'calib_dir': LC('calib_dir'),
            'model_path': LC('model_path'),
            'use_yolo': ParameterValue(LC('use_yolo'), value_type=bool),
            'vision.img_output': ParameterValue(LC('img_output'), value_type=bool),
            'vision.processing_fps': ParameterValue(LC('processing_fps'), value_type=float),
            'publish_debug_image': ParameterValue(LC('publish_debug_image'), value_type=bool),
            'params_file': LC('params_file'),
            'publish_projection': ParameterValue(LC('publish_projection'), value_type=bool),
            'camera.altura_m': ParameterValue(LC('camera_altura_m'), value_type=float),
            'camera.pitch_rad': ParameterValue(LC('camera_pitch_rad'), value_type=float),
        }],
    )

    actions = args + [camera, vision]
    if _has_pkg('my_package'):
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('my_package'), 'launch', 'robot_launch.py')),
            condition=IfCondition(LC('start_webots')),
        ))
    return LaunchDescription(actions)
