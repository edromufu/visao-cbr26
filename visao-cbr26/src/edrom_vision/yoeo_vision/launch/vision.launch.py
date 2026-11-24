# vision.launch.py: usb_cam + nó de visão (YOLO26n + segmentação clássica)

import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('yoeo_vision')
    usb_cam_params = os.path.join(share, 'config', 'usb_cam.yaml')
    vision_params = os.path.join(share, 'config', 'yoeo_vision.yaml')
    with open(usb_cam_params) as f:
        usb_cam_cfg = next(iter(yaml.safe_load(f).values()))['ros__parameters']

    return LaunchDescription([
        DeclareLaunchArgument(
            'video_device', default_value=usb_cam_cfg['video_device'],
            description='Dispositivo da câmera USB'),
        DeclareLaunchArgument(
            'camera_name', default_value=usb_cam_cfg['camera_name'],
            description='Câmera usada (verri ou milare): escolhe o arquivo de calibração'),
        DeclareLaunchArgument(
            'camera_info_url',
            default_value=['package://yoeo_vision/config/',
                           LaunchConfiguration('camera_name'), '_camera-info.yaml'],
            description='URL do YAML de calibração intrínseca da câmera'),
        DeclareLaunchArgument(
            'rotate_180', default_value=str(usb_cam_cfg.get('rotate_180', False)),
            description='Gira a imagem 180 graus antes da visão (câmera de cabeça para baixo). '
                        'Padrão: rotate_180 do config/usb_cam.yaml'),
        DeclareLaunchArgument(
            'model_path', default_value='',
            description='Modelo .pt ou pasta *_openvino_model (vazio = modelo/yolov26n-edrom.pt)'),
        DeclareLaunchArgument(
            'classic_seg', default_value='true',
            description='Liga a segmentação clássica de campo, borda e linhas'),
        DeclareLaunchArgument(
            'wb_file', default_value='',
            description='JSON de balanço de branco do wb_calib (vazio = desligado)'),
        DeclareLaunchArgument(
            'show_window', default_value='false',
            description='Abre janela do OpenCV com o overlay (precisa de monitor)'),

        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            namespace='camera',
            output='screen',
            # usb_cam.yaml primeiro; o dict abaixo sobrescreve com os argumentos do launch
            parameters=[usb_cam_params, {
                'use_sim_time': False,
                'camera_name': LaunchConfiguration('camera_name'),
                'video_device': LaunchConfiguration('video_device'),
                'camera_info_url': LaunchConfiguration('camera_info_url'),
            }],
        ),

        Node(
            package='yoeo_vision',
            executable='vision',
            name='vision',
            output='screen',
            parameters=[vision_params, {
                'use_sim_time': False,
                'rotate_180': ParameterValue(LaunchConfiguration('rotate_180'), value_type=bool),
                'model_path': ParameterValue(LaunchConfiguration('model_path'), value_type=str),
                'classic_seg': ParameterValue(LaunchConfiguration('classic_seg'), value_type=bool),
                'wb_file': ParameterValue(LaunchConfiguration('wb_file'), value_type=str),
                'show_window': ParameterValue(LaunchConfiguration('show_window'), value_type=bool),
            }],
        ),
    ])
