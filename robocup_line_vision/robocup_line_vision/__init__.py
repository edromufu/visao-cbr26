"""
robocup_line_vision: visão por estrutura de linhas + YOLO para a EDROM.

Implementa o artigo "Line Structure-based Localization for Soccer Robots"
(Schulz, Liu, Stückler, Behnke, Humanoids 2009):

- III-A e III-B: código original em ``vendor/`` (via ``stage1_adapter``);
- III-C: ``graph_nodes`` (nós e conexões);
- IV-A: ``crossings`` (cruzamentos L/T/X);
- IV-B: ``lines`` (linhas por split-and-merge) e ``ellipses`` (círculo);
- fusão com o YOLO: ``fusion``.

O núcleo não depende de ROS. O nó ROS 2 fica em ``ros/``.
"""

__version__ = '0.1.0'
