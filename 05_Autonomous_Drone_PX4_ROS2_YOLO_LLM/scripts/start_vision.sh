#!/usr/bin/env bash
# Autonomous Drone Vision & Camera Bridge Launcher
set -e

source /opt/ros/jazzy/setup.bash
source /opt/px4_ros2/install/setup.bash

# Automatically discover active Gazebo camera topic
echo "🔍 Discovering active Gazebo camera topic..."
GZ_CAMERA_TOPIC=$(gz topic -l 2>/dev/null | grep -m 1 "camera/image$" || true)

if [ -z "$GZ_CAMERA_TOPIC" ]; then
    WORLD_NAME="${PX4_GZ_WORLD:-drone_obstacle_world}"
    MODEL_NAME="x500_mono_cam_0"
    GZ_CAMERA_TOPIC="/world/${WORLD_NAME}/model/${MODEL_NAME}/link/camera_link/sensor/camera/image"
fi

echo "======================================================================"
echo "👁️ Starting Drone Onboard Camera Bridge & YOLOv8 Vision Perception"
echo "📷 Bridging: ${GZ_CAMERA_TOPIC} -> /camera/image_raw"
echo "🧠 Neural Network: Ultralytics YOLOv8 Nano Real-time Detector"
echo "======================================================================"

# Start ROS 2 Gazebo Parameter Bridge in background
ros2 run ros_gz_bridge parameter_bridge "${GZ_CAMERA_TOPIC}@sensor_msgs/msg/Image[gz.msgs.Image" --ros-args -r "${GZ_CAMERA_TOPIC}:=/camera/image_raw" &

BRIDGE_PID=$!
sleep 2

# Cleanup on exit
trap "kill -9 $BRIDGE_PID 2>/dev/null || true" EXIT

# Start YOLOv8 Vision Detector
python3 /workspace/scripts/drone_vision_detector.py
