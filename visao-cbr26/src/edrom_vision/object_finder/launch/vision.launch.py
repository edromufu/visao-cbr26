# vision.launch.py (Versão Unificada)
#
# Robô real (usb_cam):      ros2 launch object_finder vision.launch.py
# Simulação (Webots/AUREA): ros2 launch object_finder vision.launch.py simulacao:=true [start_webots:=True]
# Calibração de cor: a de object_finder/config/ (reescrita pelo `ros2 run object_finder calibrador`).

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import yaml

# Tópicos da câmera do robô AUREA no Webots
SIM_IMAGE_TOPIC = '/AUREA/camera_optical_frame/image_color'
SIM_INFO_TOPIC = '/AUREA/camera_optical_frame/camera_info'


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
    simulacao = LC('simulacao')
    sim_time = ParameterValue(simulacao, value_type=bool)

    def topico(sim, real):
        return PythonExpression(["'", sim, "' if '", simulacao, "'.lower() == 'true' else '", real, "'"])

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

        DeclareLaunchArgument('rotate_180', default_value=str(usb_cam_cfg.get('rotate_180', False)),
                              description='Gira a imagem 180 graus antes da visão (câmera de cabeça para baixo). '
                                          'Padrão: rotate_180 do config/usb_cam.yaml; no Webots use false'),

        # Simulação
        DeclareLaunchArgument('simulacao', default_value='false',
                              description='true = câmera do Webots (AUREA) em vez do usb_cam'),
        DeclareLaunchArgument('start_webots', default_value='False',
                              description='Com simulacao:=true, sobe o Webots + driver do AUREA '
                                          '(my_package/robot_launch.py)'),

        # Visão (estrutura de linhas + YOLO)
        DeclareLaunchArgument('calib_dir', default_value=os.path.join(share, 'config'),
                              description='Pasta com green_pixels.csv e white_pixels.csv (calibração de cor); '
                                          'padrão: config/, reescrita pelo calibrador'),
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
        condition=UnlessCondition(simulacao),
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
            'image_topic': topico(SIM_IMAGE_TOPIC, '/camera/image_raw'),
            'camera_info_topic': topico(SIM_INFO_TOPIC, '/camera/camera_info'),
            'calib_dir': LC('calib_dir'),
            'model_path': LC('model_path'),
            'use_yolo': ParameterValue(LC('use_yolo'), value_type=bool),
            'rotate_180': ParameterValue(LC('rotate_180'), value_type=bool),
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
            condition=IfCondition(PythonExpression([
                "'", simulacao, "'.lower() == 'true' and '", LC('start_webots'), "'.lower() == 'true'"])),
        ))
    return LaunchDescription(actions)
