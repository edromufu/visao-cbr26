#!/usr/bin/env bash
# Launcher da visão no robô.
#   ./robot.sh setup            1x (precisa de internet): dependências
#   ./robot.sh build            compila o workspace visao-cbr26/
#   ./robot.sh calibrate MODO   calibra as cores com a câmera do robô: hsv | snapshot (veja o README)
#   ./robot.sh [run] [args]     compila (se preciso) e executa; args = argumentos do vision.launch.py
# Exemplos:
#   ./robot.sh run show_window:=false
#   MODEL=/home/robo/pesos/best.pt ./robot.sh run
#   ./robot.sh run simulacao:=true
#   ./robot.sh calibrate hsv --source /dev/video2
# Variáveis: ROS_DISTRO (humble) | MODEL (best.pt de object_finder/modelo) | NOBUILD=1
#            CALIB_DIR (visao-cbr26/calibracao: onde o calibrate grava e o run lê) | NOCALIB=1 (run ignora a calibração)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISTRO="${ROS_DISTRO:-humble}"
WS="$REPO/visao-cbr26"
PKG="object_finder"
MODEL="${MODEL:-best.pt}"
CALIB_DIR="${CALIB_DIR:-$WS/calibracao}"

die() { echo "ERRO: $*" >&2; exit 1; }
source_ros() {
  [ -f "/opt/ros/$DISTRO/setup.bash" ] || die "ROS 2 $DISTRO não encontrado em /opt/ros/$DISTRO"
  set +u; source "/opt/ros/$DISTRO/setup.bash"; set -u
}
source_ws() { [ -f "$WS/install/setup.bash" ] && { set +u; source "$WS/install/setup.bash"; set -u; } || true; }

cmd_setup() {
  source_ros
  for c in git colcon rosdep pip3; do
    command -v "$c" >/dev/null || die "'$c' ausente. Instale: sudo apt install git python3-pip python3-colcon-common-extensions python3-rosdep ros-$DISTRO-tf2-ros ros-$DISTRO-usb-cam"
  done
  [ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || sudo rosdep init
  rosdep update
  cd "$WS"
  rosdep install --from-paths src --ignore-src -r -y
  pip3 install --user -r "$WS/requirements.txt" \
    || pip3 install --user --break-system-packages -r "$WS/requirements.txt"
  echo "setup OK. Rode ./robot.sh"
}

cmd_build() {
  source_ros
  cd "$WS"
  if [ -d install/soccer_vision_2d_msgs ]; then
    colcon build --symlink-install --packages-select "$PKG"
  else
    colcon build --symlink-install
  fi
}

cmd_calibrate() {
  [ $# -ge 1 ] || die "uso: ./robot.sh calibrate {hsv|snapshot} [opções]  (veja o README)"
  # sem ROS e sem build: roda direto do código-fonte
  exec env PYTHONPATH="$WS/src/edrom_vision/$PKG${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m "$PKG.pipeline.calibrate" "$@" --out "$CALIB_DIR"
}

cmd_run() {
  [ "${NOBUILD:-0}" = 1 ] || cmd_build
  source_ros; source_ws
  local extra=()
  if [ "${NOCALIB:-0}" != 1 ] && [ -f "$CALIB_DIR/hsv_params.yaml" ]; then
    extra+=("params_file:=$CALIB_DIR/hsv_params.yaml")
    echo "calibração de cor: $CALIB_DIR/hsv_params.yaml"
  else
    echo "AVISO: sem calibração de cor ($CALIB_DIR/hsv_params.yaml): usando o verde do Webots." >&2
  fi
  exec ros2 launch "$PKG" vision.launch.py model_file:="$MODEL" ${extra[@]+"${extra[@]}"} "$@"
}

case "${1:-run}" in
  setup) cmd_setup ;;
  build) cmd_build ;;
  calibrate) shift; cmd_calibrate "$@" ;;
  run)   shift || true; cmd_run "$@" ;;
  *)     cmd_run "$@" ;;   # ./robot.sh show_window:=false também funciona
esac
