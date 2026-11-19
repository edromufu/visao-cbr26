"""
Aplica a calibração do calibrador HTML (o ``calib_*.json`` que ele baixa).

Regenera os CSVs a partir do JSON (o do verde pode ter alguns MB), no mesmo
formato do calibrador OpenCV, e SOBRESCREVE a calibração em object_finder/config/
(src/ e install/), que é a que o vision.launch usa::

    ros2 run object_finder importar_calibracao ~/Downloads/calib_20261113_091500.json

Com ``--saida PASTA`` também guarda um histórico datado (``calib_<data>/`` + ``ultima/``).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from typing import Optional, Sequence

from . import core


def _ler(json_path: Path) -> tuple:
    """Lê o JSON do calibrador HTML: devolve (calibração, data de criação)."""
    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    cal = core.Calibration.from_dict(data)
    cal.observacoes = (cal.observacoes + ' ' if cal.observacoes else '') + \
        f'importada de {Path(json_path).name} (origem: {data.get("origem", "?")})'
    when = None
    if data.get('criada_em'):
        try:
            when = dt.datetime.fromisoformat(str(data['criada_em'])[:19])
        except ValueError:
            when = None
    return cal, when


def importar(json_path: Path, out_root: Path) -> Path:
    """Lê o JSON e grava ``out_root/calib_<data>/`` + ``ultima/``."""
    cal, when = _ler(json_path)
    return core.save_calibration(cal, out_root, now=when)


def importar_para_config(json_path: Path, dirs) -> list:
    """Lê o JSON e sobrescreve a calibração nas pastas ``config/``."""
    cal, when = _ler(json_path)
    return core.save_to_config(cal, dirs, now=when)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ponto de entrada."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('json')
    ap.add_argument('--saida', default=None, help='opcional: também guarda histórico datado aqui')
    ap.add_argument('--sem-config', action='store_true', help='não grava em object_finder/config')
    a = ap.parse_args(argv)
    if not a.sem_config:
        for d in importar_para_config(Path(a.json), core.config_dirs()):
            print(f'calibracao gravada em {d}')
    if a.saida:
        d = importar(Path(a.json), Path(a.saida))
        print(f'calibracao gravada em {d} (e em {Path(a.saida) / "ultima"})')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
