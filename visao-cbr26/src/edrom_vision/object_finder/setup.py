from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'object_finder'
__version__ = '0.0.1'

setup(
    name=package_name,
    version=__version__,
    
    packages=find_packages(exclude=['docs', 'tests*']),
    
    # data_files informa ao colcon quais arquivos adicionais instalar.
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Instala o nosso launch file unificado
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        
        # Instala os pesos (.pt e .onnx) que estiverem em modelo/
        (os.path.join('share', package_name, 'modelo'), glob('modelo/*.pt') + glob('modelo/*.onnx')),
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),

        # Instala a config da câmera (usb_cam.yaml), os parâmetros da visão e as calibrações
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml') + glob('config/*.csv')),
    ],
    
    # install_requires lista as dependências de Python que o pip deve instalar.
    install_requires=['setuptools', 'numpy', 'opencv-python', 'pandas', 'ultralytics'],
    extras_require={'onnx': ['onnx', 'onnxruntime'], 'dev': ['pytest']},
    
    zip_safe=True,
    description='Pacote de detecção de objetos para a EDROM',
    long_description='Detecta bola, robôs e interseções com YOLO, valida as detecções pela segmentação do campo (HSV) e publica a fronteira do campo e os obstáculos.',
    license='MIT',
    
    entry_points={
        'console_scripts': [
            # Certifique-se de que o nome do arquivo aqui é o nome do seu script unificado final.
            'finder = object_finder.connecting_and_showing:main',
            # segmentação sem ROS em imagem, vídeo ou câmera (= python3 -m object_finder.pipeline)
            'segmentar = object_finder.pipeline.__main__:main',
            # benchmark/acurácia entre modelos e receita de treino do YOLO26n
            'comparar_modelos = object_finder.tools.compare_models:main',
            'treinar_yolo26n = object_finder.tools.train_yolo26n:main',
        ],
    },
    
    author='EDROM',
)