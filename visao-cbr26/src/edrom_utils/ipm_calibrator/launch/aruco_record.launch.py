"""Inicia a câmera (mesma config do vision.launch) e o aruco_record."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import yaml


def generate_launch_description():
    # Mesmo usb_cam.yaml do vision.launch e do camera_calibrator
    usb_cam_params = os.path.join(
        get_package_share_directory('object_finder'), 'config', 'usb_cam.yaml')
    with open(usb_cam_params) as f:
        camera_name = next(iter(yaml.safe_load(f).values()))['ros__parameters']['camera_name']

    return LaunchDescription([
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
            remappings=[
                ('image_raw', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
            ],
        ),
    ])
