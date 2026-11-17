
import argparse
import os
import signal
import subprocess
import tarfile
import time
from pathlib import Path

import yaml
from ament_index_python.packages import get_package_prefix

TARBALL = '/tmp/calibrationdata.tar.gz'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', default='8x6')
    parser.add_argument('--square', default='0.025')
    args = parser.parse_args()

    # <ws>/install/camera_calibrator -> <ws>
    ws = Path(get_package_prefix('camera_calibrator')).parents[1]
    # Mesma pasta que o object_finder instala e o vision.launch lê
    files = ws / 'src/edrom_vision/object_finder/config'
    params_file = files / 'usb_cam.yaml'

    # camera_name (verri ou milare) vem do usb_cam.yaml
    params = yaml.safe_load(params_file.read_text())
    camera_name = next(iter(params.values()))['ros__parameters']['camera_name']

    if os.path.exists(TARBALL):
        os.remove(TARBALL)

    camera = subprocess.Popen([
        'ros2', 'run', 'usb_cam', 'usb_cam_node_exe',
        '--ros-args', '-r', '__ns:=/camera', '--params-file', str(params_file),
    ])
    time.sleep(2)
    if camera.poll() is not None:
        raise SystemExit('usb_cam não iniciou. A câmera já está em uso (vision.launch rodando?)')

    try:
        subprocess.run([
            'ros2', 'run', 'camera_calibration', 'cameracalibrator',
            '--size', args.size,
            '--square', args.square,
            '--camera_name', camera_name,
            '--no-service-check',
            '--ros-args', '-r', 'image:=/camera/image_raw',
        ])
    finally:
        camera.send_signal(signal.SIGINT)
        camera.wait()

    if not os.path.exists(TARBALL):
        raise SystemExit('Nada salvo: clique em SAVE antes de sair.')

    output = files / f'{camera_name}_camera-info.yaml'
    with tarfile.open(TARBALL) as tar:
        output.write_bytes(tar.extractfile('ost.yaml').read())
    print(f'Calibração salva em {output}')


if __name__ == '__main__':
    main()