"""Gera robocup_line_vision/calibration/calibrador.html (arquivo único, offline)."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'robocup_line_vision' / 'calibration' / 'calibrador.html'

if __name__ == '__main__':
    tpl = (HERE / 'calibrador_template.html').read_text(encoding='utf-8')
    core = (HERE / 'calibrador_core.js').read_text(encoding='utf-8')
    assert '/*__CORE__*/' in tpl
    OUT.write_text(tpl.replace('/*__CORE__*/', core), encoding='utf-8')
    print(f'gerado {OUT} ({OUT.stat().st_size} bytes)')
