"""
Leva uma calibração de cor (feita com o calibrar_cores) para o nó de visão.

    ros2 run object_finder aplicar_calibracao_cores                       # ~/calibracoes/ultima
    ros2 run object_finder aplicar_calibracao_cores ~/calibracoes/calib_20261119_210000
    ros2 run object_finder aplicar_calibracao_cores --ao-vivo             # também no nó rodando

O calibrador salva uma caixa HSV para o verde (carpete) e outra para o branco
(linhas). Este comando grava essas caixas como os parâmetros do nó:

    verde  -> hsv.field_min / hsv.field_max
    branco -> hsv.white_min / hsv.white_max   (o nó usa o branco também como marcação)

em ``config/hsv_calibrado.yaml`` do object_finder (no código-fonte). O
vision.launch carrega esse arquivo depois do vision_params.yaml, se ele
existir. Depois de gravar, rode ``colcon build --packages-select object_finder``
para instalar o arquivo.

Com ``--ao-vivo`` as faixas também são aplicadas no nó ``/vision`` em execução
(sem reiniciar), de uma vez só: se o nó recusar, nada muda.

Por que não usar o green_pixels.csv do calibrador: o nó deriva a faixa do
verde do CSV com uma margem extra (8, 40, 50), o que alargaria a caixa
calibrada. Os parâmetros hsv.* usam a caixa exata.
"""

import argparse
import json
from pathlib import Path
import sys

import yaml

NO_PADRAO = '/vision'


def ler_faixas(pasta: Path) -> dict:
    """Lê o calib*.json da pasta e devolve os parâmetros hsv.* (listas de 3 ints)."""
    jsons = sorted(pasta.glob('calib*.json'))
    if not jsons:
        raise SystemExit(f'nenhum calib*.json em {pasta} (rode o calibrar_cores e salve com S)')
    with open(jsons[0], encoding='utf-8') as fh:
        calib = json.load(fh)
    faixas = {}
    for classe, nome in (('verde', 'field'), ('branco', 'white')):
        lower = [int(v) for v in calib[classe]['lower']]
        upper = [int(v) for v in calib[classe]['upper']]
        faixas[f'{nome}_min'], faixas[f'{nome}_max'] = lower, upper
    return faixas


def pasta_config_fonte() -> Path:
    """config/ do object_finder no código-fonte (onde fica o vision_params.yaml)."""
    from ament_index_python.packages import get_package_prefix

    # <ws>/install/object_finder -> <ws>; o src pode estar em <ws>/src ou <ws>/*/src
    ws = Path(get_package_prefix('object_finder')).parents[1]
    config = Path('edrom_vision/object_finder/config')
    candidatos = [ws / 'src' / config, *sorted(ws.glob(f'*/src/{config}'))]
    for c in candidatos:
        if (c / 'vision_params.yaml').is_file():
            return c
    raise SystemExit('config/ do object_finder não encontrado. Procurei em:\n  '
                     + '\n  '.join(map(str, candidatos)) + '\nUse --destino.')


def gravar_yaml(destino: Path, faixas: dict, origem: Path) -> None:
    conteudo = {'vision': {'ros__parameters': {'hsv': faixas}}}
    cabecalho = (
        f'# Gerado por aplicar_calibracao_cores a partir de {origem}\n'
        '# Carregado pelo vision.launch depois do vision_params.yaml (sobrescreve o hsv de lá).\n'
        '# Apague este arquivo para voltar às faixas padrão.\n')
    destino.write_text(cabecalho + yaml.safe_dump(conteudo, default_flow_style=None,
                                                  sort_keys=False))


def aplicar_ao_vivo(faixas: dict, no: str) -> bool:
    """Aplica as faixas no nó em execução, de uma vez (set_parameters_atomically)."""
    import rclpy
    from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
    from rcl_interfaces.srv import SetParametersAtomically

    rclpy.init()
    node = rclpy.create_node('aplicar_calibracao_cores')
    try:
        cli = node.create_client(SetParametersAtomically, f'{no}/set_parameters_atomically')
        if not cli.wait_for_service(timeout_sec=3.0):
            print(f'nó {no} não encontrado (o vision.launch está rodando?)')
            return False
        req = SetParametersAtomically.Request()
        req.parameters = [
            Parameter(name=f'hsv.{nome}', value=ParameterValue(
                type=ParameterType.PARAMETER_INTEGER_ARRAY, integer_array_value=valor))
            for nome, valor in faixas.items()]
        futuro = cli.call_async(req)
        rclpy.spin_until_future_complete(node, futuro, timeout_sec=5.0)
        res = futuro.result()
        if res is None:
            print(f'sem resposta do nó {no}')
            return False
        if not res.result.successful:
            print(f'o nó {no} recusou as faixas: {res.result.reason}')
            return False
        print(f'faixas aplicadas no nó {no} (sem reiniciar)')
        return True
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description='Leva a calibração de cor (calibrar_cores) para os parâmetros hsv.* do nó.')
    ap.add_argument('calib', nargs='?', default=str(Path.home() / 'calibracoes' / 'ultima'),
                    help='pasta da calibração (padrão: ~/calibracoes/ultima)')
    ap.add_argument('--destino', default=None,
                    help='yaml de saída (padrão: config/hsv_calibrado.yaml do object_finder)')
    ap.add_argument('--ao-vivo', action='store_true',
                    help='também aplica no nó de visão em execução')
    ap.add_argument('--no', default=NO_PADRAO, help=f'nó de visão (padrão: {NO_PADRAO})')
    a = ap.parse_args(argv)

    pasta = Path(a.calib).expanduser()
    faixas = ler_faixas(pasta)
    for nome, valor in faixas.items():
        print(f'  hsv.{nome}: {valor}')

    destino = Path(a.destino).expanduser() if a.destino else (
        pasta_config_fonte() / 'hsv_calibrado.yaml')
    gravar_yaml(destino, faixas, pasta)
    print(f'gravado em {destino}')
    if not a.destino:
        print('rode "colcon build --packages-select object_finder" para o vision.launch usar.')

    if a.ao_vivo and not aplicar_ao_vivo(faixas, a.no):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
