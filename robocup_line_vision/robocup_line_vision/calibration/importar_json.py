"""
Recria uma calibração versionada a partir do JSON do calibrador HTML.

O HTML baixa ``calib_*.json`` + CSVs. Se preferir não lidar com os CSVs (o do
verde pode ter alguns MB), este comando regenera tudo a partir do JSON, no
mesmo formato do calibrador OpenCV, e atualiza ``ultima/``::

    python3 -m robocup_line_vision.calibration.importar_json ~/Downloads/calib_20261113_091500.json \
        --saida calibracoes
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from typing import Optional, Sequence

from . import core


def importar(json_path: Path, out_root: Path) -> Path:
    """Lê o JSON e grava ``out_root/calib_<data>/`` + ``ultima/``."""
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
    return core.save_calibration(cal, out_root, now=when)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ponto de entrada."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('json')
    ap.add_argument('--saida', default='calibracoes')
    a = ap.parse_args(argv)
    d = importar(Path(a.json), Path(a.saida))
    print(f'calibracao gravada em {d} (e em {Path(a.saida) / "ultima"})')
    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
