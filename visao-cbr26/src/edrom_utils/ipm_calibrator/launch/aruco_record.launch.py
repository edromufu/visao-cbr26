"""Inicia a câmera (mesma config do vision.launch) e o aruco_record."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import yaml


def generate_launch_description():
    # Mesmo usb_cam.yaml do vision.launch e do camera_calibrator
    usb_cam_params = os.path.join(
        get_package_share_directory('object_finder'), 'config', 'usb_cam.yaml')
    with open(usb_cam_params) as f:
        cam_cfg = next(iter(yaml.safe_load(f).values()))['ros__parameters']
    camera_name = cam_cfg['camera_name']

    return LaunchDescription([
        DeclareLaunchArgument(
            'rotate_180',
            default_value=str(cam_cfg.get('rotate_180', False)),
            description='Gira a janela 180 graus (câmera de cabeça para baixo). '
                        'Padrão: rotate_180 do config/usb_cam.yaml',
        ),
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            namespace='camera',
            output='screen',
            parameters=[usb_cam_params, {
                'camera_info_url':
                    f'package://object_finder/config/{camera_name}_camera-info.yaml',
            }],
        ),
        Node(
            package='ipm_calibrator',
            executable='aruco_record',
            output='screen',
            parameters=[{
                'rotate_180': ParameterValue(
                    LaunchConfiguration('rotate_180'), value_type=bool),
            }],
            remappings=[
                ('image_raw', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
            ],
        ),
    ])
