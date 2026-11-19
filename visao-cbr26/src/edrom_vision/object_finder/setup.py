from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'object_finder'
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
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Instala o launch file
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),

        # Instala o modelo .pt
        (os.path.join('share', package_name, 'modelo'), glob('modelo/*.pt')),
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),

        # Config da câmera (usb_cam.yaml), calibração da câmera, limiares (params.yaml) e
        # calibração de cor (green/white_pixels.csv + calib.json, reescritos pelo calibrador)
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml') + glob('config/*.csv') + glob('config/*.json')),

        # Calibração de cor padrão (Webots): green_pixels.csv e white_pixels.csv
        (os.path.join('share', package_name, 'calib', 'padrao_webots'), glob('calib/padrao_webots/*')),
    ],

    # ultralytics é opcional (sem ele: use_yolo:=false ou modelo .onnx com onnxruntime).
    install_requires=['setuptools', 'numpy', 'opencv-python', 'scipy', 'pandas', 'pyyaml', 'ultralytics'],

    zip_safe=True,
    description='Pacote de visão da EDROM: YOLO + estrutura de linhas do campo',
    long_description='Detecção de objetos (YOLO) integrada à segmentação das linhas do campo fiel ao artigo '
                     'Line Structure-based Localization for Soccer Robots (Schulz et al., 2009).',
    license='MIT',

    entry_points={
        'console_scripts': [
            'finder = object_finder.connecting_and_showing:main',
            'line_vision = object_finder.__main__:main',
            'calibrador = object_finder.calibration.calibrator_cv:main',
            'importar_calibracao = object_finder.calibration.importar_json:main',
            'capture_frames = object_finder.calibration.capture_frames:main',
            'capture_frames_ros = object_finder.calibration.capture_frames_ros:main',
        ],
    },

    author='EDROM',
)
