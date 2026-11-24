import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'yoeo_vision'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'modelo'), glob('modelo/*.pt')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='EDROM',
    maintainer='EDROM',
    maintainer_email='edromufu@gmail.com',
    description='Visao da EDROM: YOLO26n (deteccao) + segmentacao classica de campo e linhas',
    license='MIT',
    entry_points={
        'console_scripts': [
            'vision = yoeo_vision.vision_node:main',
        ],
    },
)
