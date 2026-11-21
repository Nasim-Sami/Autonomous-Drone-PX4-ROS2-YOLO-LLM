#!/usr/bin/env bash
# Runner script for Autonomous Drone Container
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
IMAGE_NAME="drone_jazzy_sim:latest"
CONTAINER_NAME="drone_jazzy_sim_instance"

# Allow local root/docker to access the host X11 display
xhost +local:root 2>/dev/null || true
xhost +local:docker 2>/dev/null || true

echo "=========================================================="
echo "🚁 Starting Drone Simulation Container: ${CONTAINER_NAME}"
echo "🎮 Hardware GPU Acceleration: NVIDIA Container Toolkit / /dev/dri enabled"
echo "📁 Workspace Mount: ${WORKSPACE_ROOT} -> /workspace"
echo "=========================================================="

# Check for NVIDIA GPU support
GPU_FLAGS=()
if command -v nvidia-smi &>/dev/null && docker run --rm --gpus all ubuntu nvidia-smi &>/dev/null; then
    echo "⚡ NVIDIA GPU detected and supported by Docker runtime. Enabling --gpus all."
    GPU_FLAGS+=(
        --gpus all
        --env "NVIDIA_VISIBLE_DEVICES=all"
        --env "NVIDIA_DRIVER_CAPABILITIES=all"
        --env "__NV_PRIME_RENDER_OFFLOAD=1"
        --env "__GLX_VENDOR_LIBRARY_NAME=nvidia"
    )
elif [ -d /dev/dri ]; then
    echo "⚠️ NVIDIA container runtime not active. Falling back to /dev/dri acceleration."
    GPU_FLAGS+=(--device=/dev/dri)
fi

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "🔄 Resuming existing persistent container: ${CONTAINER_NAME}..."
    docker start -ai "${CONTAINER_NAME}"
else
    echo "🚀 Creating and launching persistent container: ${CONTAINER_NAME}..."
    docker run -it \
        --name "${CONTAINER_NAME}" \
        --net=host \
        --ipc=host \
        "${GPU_FLAGS[@]}" \
        --env="DISPLAY=${DISPLAY:-:0}" \
        --env="QT_X11_NO_MITSHM=1" \
        --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
        --volume="${WORKSPACE_ROOT}:/workspace" \
        "${IMAGE_NAME}" \
        /bin/bash
fi
