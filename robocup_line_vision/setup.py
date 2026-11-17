from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'robocup_line_vision'
__version__ = '0.1.0'

setup(
    name=package_name,
    version=__version__,
    packages=find_packages(exclude=['test', 'tools', 'tools.*']),
    # Dados do pacote Python: CSVs originais (vendor) e o calibrador HTML.
    package_data={
        package_name: ['vendor/*.csv', 'vendor/VENDOR.md', 'calibration/calibrador.html'],
    },
    # data_files informa ao colcon quais arquivos adicionais instalar.
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(
            os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'modelo'), glob('modelo/*.pt')),
        (os.path.join('share', package_name, 'calib', 'padrao_webots'), glob('calib/padrao_webots/*')),
        (os.path.join('share', package_name, 'docs'), glob('docs/*.md')),
    ],
    # ultralytics é opcional (sem ele: --sem-yolo ou modelo .onnx com onnxruntime).
    install_requires=['setuptools', 'numpy', 'opencv-python', 'scipy', 'pandas', 'pyyaml'],
    zip_safe=True,
    maintainer='EDROM',
    maintainer_email='edromufu@gmail.com',
    description='Visao por estrutura de linhas + YOLO para a EDROM',
    long_description='Segmentacao das linhas do campo fiel ao artigo Line Structure-based Localization '
                     'for Soccer Robots (Schulz et al., 2009) integrada ao detector YOLO.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'line_vision_node = robocup_line_vision.ros.line_vision_node:main',
            'capture_frames_ros = robocup_line_vision.calibration.capture_frames_ros:main',
            'calibrador = robocup_line_vision.calibration.calibrator_cv:main',
            'capture_frames = robocup_line_vision.calibration.capture_frames:main',
            'line_vision = robocup_line_vision.__main__:main',
        ],
    },
)
