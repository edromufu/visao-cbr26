# sim.launch.py — simulação (Webots + nó de visão + soccer_ipm)
#
# Uso:
#   ros2 launch robocup_line_vision sim.launch.py                    # só visão + ipm (Webots já rodando)
#   ros2 launch robocup_line_vision sim.launch.py start_webots:=True  # sobe também o my_package (AUREA)
#

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('robocup_line_vision')
    args = [
        DeclareLaunchArgument('start_webots', default_value='False',
                              description='Sobe o Webots + driver do AUREA (my_package/robot_launch.py)'),
        DeclareLaunchArgument(
            'image_topic', default_value='/AUREA/camera_optical_frame/image_color'),
        DeclareLaunchArgument('camera_info_topic',
                              default_value='/AUREA/camera_optical_frame/camera_info'),
        DeclareLaunchArgument('calib_dir', default_value=os.path.join(share, 'calib', 'padrao_webots'),
                              description='Pasta com green_pixels.csv e white_pixels.csv'),
        DeclareLaunchArgument('model_path', default_value=os.path.join(
            share, 'modelo', 'best.pt')),
        DeclareLaunchArgument('use_yolo', default_value='True'),
        DeclareLaunchArgument('img_output', default_value='False',
                              description='Janela OpenCV com o overlay'),
        DeclareLaunchArgument('publish_landmarks', default_value='False'),
        DeclareLaunchArgument('use_ipm', default_value='True'),
    ]
    webots = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('my_package'), 'launch', 'robot_launch.py')),
        condition=IfCondition(LaunchConfiguration('start_webots')),
    ) if _has_pkg('my_package') else None
    vision = Node(
        package='robocup_line_vision',
        executable='line_vision_node',
        name='line_vision_node',
        output='screen',
        emulate_tty=True,
        parameters=[
            {'use_simulation': True},
            {'use_sim_time': True},
            {'image_topic': LaunchConfiguration('image_topic')},
            {'camera_info_topic': LaunchConfiguration('camera_info_topic')},
            {'calib_dir': LaunchConfiguration('calib_dir')},
            {'model_path': LaunchConfiguration('model_path')},
            {'use_yolo': LaunchConfiguration('use_yolo')},
            {'vision.img_output': LaunchConfiguration('img_output')},
            {'publish_landmarks': LaunchConfiguration('publish_landmarks')},
            {'params_file': os.path.join(share, 'config', 'params.yaml')},
            {'camera.altura_m': 0.70},
            {'camera.pitch_rad': 0.0},
        ],
    )
    # mesmo bloco do vision.launch.py do Webots_YOLOv8
    soccer_ipm = Node(
        package='soccer_ipm',
        executable='ipm',
        name='soccer_ipm_node',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_ipm')),
        parameters=[
            {'use_sim_time': True},
            {'output_frame': 'base_link'},
            {'camera_frame': 'camera_optical_frame'},
            {'balls.ball_diameter': 0.14},
            {'use_distortion': False},
        ],
        remappings=[
            ('camera/image_raw', LaunchConfiguration('image_topic')),
            ('camera_info', LaunchConfiguration('camera_info_topic')),
        ],
    )
    actions = args + ([webots] if webots else []) + [vision, soccer_ipm]
    return LaunchDescription(actions)


def _has_pkg(name):
    try:
        get_package_share_directory(name)
        return True
    except Exception:  # noqa: BLE001
        return False
