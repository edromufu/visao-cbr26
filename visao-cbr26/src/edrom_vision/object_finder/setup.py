import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'object_finder'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'modelo'), glob('modelo/*.xml') + glob('modelo/*.bin')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],     # numpy, opencv e openvino vêm do requirements.txt
    zip_safe=True,
    maintainer='EDROM',
    maintainer_email='edromufu@gmail.com',
    description='Visão da EDROM com o YOEO-26n (OpenVINO) + IPM (altura fixa ou cadeia cinemática)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'finder = object_finder.yoeo_node:main',
            'ipm = object_finder.ipm_node:main',
        ],
    },
)
