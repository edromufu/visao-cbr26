# real.launch.py — robô real (câmera por índice, como o object_finder da EDROM)
#
# Uso:
#   ros2 launch robocup_line_vision real.launch.py camera_idx:=2 \
#       calib_dir:=$HOME/calibracoes/ultima img_output:=True
#

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('robocup_line_vision')
    args = [
        DeclareLaunchArgument('camera_idx', default_value='2',
                              description='Índice da webcam (EDROM usa 2)'),
        DeclareLaunchArgument('largura', default_value='640'),
        DeclareLaunchArgument('altura', default_value='480'),
        DeclareLaunchArgument('calib_dir', default_value=os.path.join(share, 'calib', 'padrao_webots'),
                              description='Pasta da calibração do dia (ex.: ~/calibracoes/ultima)'),
        DeclareLaunchArgument('model_path', default_value=os.path.join(
            share, 'modelo', 'best.pt')),
        DeclareLaunchArgument('use_yolo', default_value='True'),
        DeclareLaunchArgument('img_output', default_value='True'),
        DeclareLaunchArgument('publish_landmarks', default_value='False'),
        DeclareLaunchArgument('processing_fps', default_value='30.0'),
    ]
    vision = Node(
        package='robocup_line_vision',
        executable='line_vision_node',
        name='line_vision_node',
        output='screen',
        emulate_tty=True,
        parameters=[
            {'use_simulation': False},
            {'vision.camera_idx': LaunchConfiguration('camera_idx')},
            {'vision.largura': LaunchConfiguration('largura')},
            {'vision.altura': LaunchConfiguration('altura')},
            {'vision.img_output': LaunchConfiguration('img_output')},
            {'vision.processing_fps': LaunchConfiguration('processing_fps')},
            {'calib_dir': LaunchConfiguration('calib_dir')},
            {'model_path': LaunchConfiguration('model_path')},
            {'use_yolo': LaunchConfiguration('use_yolo')},
            {'publish_landmarks': LaunchConfiguration('publish_landmarks')},
            {'params_file': os.path.join(share, 'config', 'params.yaml')},
        ],
    )
    return LaunchDescription(args + [vision])
