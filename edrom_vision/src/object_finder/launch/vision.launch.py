# vision.launch.py (Versão Unificada)

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():


    return LaunchDescription([

        DeclareLaunchArgument(
            "video_device",
            default_value="/dev/video0",
            description="Dispositivo da câmera USB",
        ),  

        DeclareLaunchArgument(
            "camera_info_url",
            default_value ="package://object_finder/camera_calibration/ex.yaml",
            description="URL do YAML de calibração intrínseca da câmera",
        ),

        Node(
            package="usb_cam",
            executable="usb_cam_node_exe",
            name="usb_cam",
            namespace="camera",
            output="screen",
            parameters=[{
                "use_sim_time": False,
                "video_device": LaunchConfiguration("video_device"),
                "camera_info_url": LaunchConfiguration("camera_info_url"),
                "image_width": 640,
                "image_height": 480,
                "framerate": 30.0,
                "pixel_format": "yuyv2rgb",
                "frame_id": "camera_optical_frame",
            }],
        ),

        Node(
            package='object_finder',
            executable='finder', 
            name='vision',
            output='screen',
            parameters=[{
                "use_sim_time": False,
            }],
        ),
        
        Node(
            package='soccer_ipm',
            executable='ipm',
            name='soccer_ipm_node',
            output='screen',
            parameters=[{
                "use_sim_time": False,
                "output_frame": "base_footprint",
                "balls.ball_diameter": 0.14,
                "use_distortion": True,
                "goalposts.footpoint_out_of_image_threshold": 0.8,
                "robots.footpoint_out_of_image_threshold": 0.8,
            }],
            remappings=[
                ("camera_info", "/camera/camera_info"),
            ],
        ),
    ])
