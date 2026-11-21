# 🚁 Autonomous Aerial Robotics: PX4 SITL + ROS 2 Jazzy + Gazebo Harmonic + YOLOv8 + Small LLM

<div align="center">

[![ROS 2](https://img.shields.io/badge/ROS_2-Jazzy_Jalisco-22314E?style=for-the-badge&logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/)
[![PX4 Autopilot](https://img.shields.io/badge/PX4_Autopilot-v1.15_SITL-EE3322?style=for-the-badge&logo=drone&logoColor=white)](https://px4.io/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic_8.15-FF6600?style=for-the-badge&logo=gazebo&logoColor=white)](https://gazebosim.org/)
[![QGroundControl](https://img.shields.io/badge/QGroundControl-v4.4_MAVLink-007ACC?style=for-the-badge&logo=gnome-terminal&logoColor=white)](http://qgroundcontrol.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5_1.5B-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8_Nano-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](../LICENSE)
[![Developer](https://img.shields.io/badge/Developer-Nasim--Sami-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nasim-Sami)

**An end-to-end, production-grade autonomous quadcopter pipeline featuring Natural Language Mission Planning (English & Bengali), a Physics-based 3D Safety Gatekeeper, Real-time YOLOv8 Computer Vision Perception, and PX4 Offboard Trajectory Tracking.**

[System Architecture](#-system-architecture) • [Theory & Mathematics](../theory_and_mathematics/README.md) • [Key Features](#-key-features) • [Installation](#-installation--setup) • [Quick Start](#-step-by-step-execution-guide) • [Verification Tests](#-verification-and-benchmark-suite)

</div>

---

## 📖 Overview

This project implements a complete autonomous aerial robotics stack designed for real-world inspection and surveillance missions. Operators can command the quadcopter through speech or natural language text in either **English** or **Bengali** (e.g., *"Take off to 10 meters, go forward 15 meters, take a photo"* or *"সামনে ৫ মিটার যাও"*). 

The mission command is processed through an on-device Small Language Model (**Ollama `qwen2.5:1.5b`**) into structured flight primitives. Before sending any flight setpoint to the drone, a deterministic **3D Altitude-Aware Trajectory Gatekeeper** evaluates environmental perception from an onboard **Ultralytics YOLOv8** neural network and current telemetry. If an obstacle is detected in the flight corridor at low altitude, the mission is rejected with an actionable safety warning. If the drone is commanded to cruise safely above the obstacle height ($\ge 3.0\text{ m}$), safe overflight clearance is granted and the drone flies smoothly in Gazebo Harmonic while streaming telemetry to both a custom **Web Ground Station** and **QGroundControl**.

> [!TIP]
> **Mathematical & Physical Foundations Documentation:**
> For rigorous textbook derivations of the optical physics ($D = \frac{H \cdot f}{h}$), 4D Hamilton Quaternions, Euler rate singularity proofs ($\dot{\psi} = \frac{q\sin\phi+r\cos\phi}{\cos\theta}$), EKF2 Taylor-series Jacobians, and interactive 3D WebGL labs, see **[`theory_and_mathematics/`](../theory_and_mathematics/README.md)**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph UI ["Operator Interface"]
        GCS["Web Ground Station (Port 8080)<br/>Dual Voice/Type • English & Bengali"]
        QGC["QGroundControl (MAVLink)<br/>HUD • Artificial Horizon • Satellite Map"]
    end

    subgraph AI ["AI Reasoning & Safety Gatekeeper"]
        LLM["Ollama Small LLM (qwen2.5:1.5b)<br/>Natural Language Mission Decomposition"]
        GATE["3D Altitude-Aware Gatekeeper<br/>Kinematic Feasibility & Geofence (300m/150m/10m/s)"]
        GEN["10Hz NED Trajectory Generator<br/>Parametric 3D Waypoint Streamer"]
    end

    subgraph Perception ["Vision & Neural Perception"]
        CAM["Gazebo Onboard Camera<br/>x500_mono_cam Airframe 4010"]
        BRIDGE["ros_gz_bridge<br/>GZ Image ➔ /camera/image_raw"]
        YOLO["Ultralytics YOLOv8 Nano<br/>Obstacle Detection & Proximity Estimation"]
    end

    subgraph FlightStack ["ROS 2 & Autopilot Core"]
        ROS["ROS 2 Jazzy Jalisco<br/>rclpy Node Orchestration"]
        XRCE["Micro-XRCE-DDS Agent<br/>UDP Port 8888 Bridge"]
        PX4["PX4 SITL v1.15 Autopilot<br/>Offboard Control Mode • EKF2 State Estimator"]
        GZ["Gazebo Harmonic 8.15 Physics<br/>drone_obstacle_world.sdf"]
    end

    GCS -->|Speech / Text| LLM
    LLM -->|Flight Primitives JSON| GATE
    YOLO -->|Perception JSON / Obstacle Ahead| GATE
    CAM --> BRIDGE --> YOLO
    GATE -->|Approved Mission| GEN
    GEN -->|10Hz TrajectorySetpoint| ROS
    ROS <==>|uORB / DDS Topics| XRCE <==> PX4
    PX4 <==>|Lockstep / gz-sim plugins| GZ
    PX4 -.->|MAVLink UDP 18570| QGC
    ROS -->|Telemetry & Snaps| GCS
```

---

## ✨ Key Features

### 1. Dual Voice & Text Ground Control Station
- Responsive browser-based dashboard hosted at `http://localhost:8080`.
- Real-time bilingual speech recognition (English and Bengali) using Web Speech API with explicit audio-visual listening indicators (pulsing red indicator, soundwave animations, audio chimes).
- Editable transcription preview before mission dispatch.

### 2. 3D Altitude-Aware Trajectory Gatekeeper
- **10x Expanded Flight Boundaries**: Max ceiling $150.0\text{ m}$, Geofence radius $300.0\text{ m}$, Max flight speed $10.0\text{ m/s}$.
- **Vertical Overflight Logic**: If ground obstacle (human, SUV, bus) is detected at distance $< 4.0\text{ m}$:
  - If current altitude $z < 3.0\text{ m}$: **REJECTED** with obstacle warning.
  - If current altitude $z \ge 3.0\text{ m}$: **APPROVED** with logged vertical clearance.
- **State-Aware Auto-Repair**: Automatically prepends a deterministic takeoff maneuver if aerial commands are issued while the drone is grounded.

### 3. Onboard YOLOv8 Aerial Perception
- Ultralytics YOLOv8 Nano running real-time inference on the `/camera/image_raw` stream.
- Center-corridor proximity calculation and threat classification (`person`, `car`, `bus`, `truck`, `box`).
- Snapshots triggered dynamically on `"take a photo"` commands and immediately served to the web dashboard.

### 4. PX4 SITL Offboard Flight & QGroundControl HUD
- Native PX4 v1.15 offboard control via Micro-XRCE-DDS middleware.
- Full EKF2 sensor fusion: IMU, Barometer (`AirPressure`), Magnetometer (`Magnetometer`), and GPS (`NavSat`).
- Simultaneous telemetry streaming to QGroundControl for real-time aeronautical HUD, artificial horizon, and satellite map tracking.

### 5. High-Fidelity Demonstration Video
- Full-length, production-grade video demo available at **`Autonomous_Drone_PX4_ROS2_YOLO_LLM_Demo.mp4`** (1080p @ 60fps, 2m 29s).
- Features dynamic lower-third telemetry banners highlighting real-time obstacle rejection, altitude climb with clearance computation, YOLOv8 aerial reconnaissance, and bilingual voice mission dispatch.

---

## 📦 Prerequisites

- **Host OS**: Ubuntu 24.04 / 22.04 LTS (Linux x86_64)
- **Dedicated GPU**: NVIDIA RTX / GTX GPU (e.g. RTX 3050 Ti Laptop / Desktop) with proprietary NVIDIA drivers (v535+)
- **GPU Container Runtime**: NVIDIA Container Toolkit (`nvidia-container-toolkit`) configured for Docker
- **Container Engine**: Docker CE with `--gpus all` support
- **LLM Engine**: Ollama with model `qwen2.5:1.5b`
- **GCS Software**: QGroundControl (`QGroundControl.AppImage`)

---

## 🔧 Installation & Setup

### 1. Install NVIDIA Container Toolkit (Host)
To ensure Gazebo Harmonic, PX4, and YOLOv8 achieve high frame rates (60fps) without pegging the CPU, configure Docker with NVIDIA GPU acceleration:

```bash
# 1. Add NVIDIA official package repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 3. Configure Docker runtime and restart daemon
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 4. Verify GPU passthrough
docker run --rm --gpus all ubuntu nvidia-smi
```

> [!NOTE]
> On hybrid laptops (NVIDIA Optimus / ASUS TUF / ROG), verify that the discrete GPU is powered on:
> ```bash
> echo 0 | sudo tee /sys/devices/platform/asus-nb-wmi/dgpu_disable && echo 1 | sudo tee /sys/bus/pci/rescan
> ```

### 2. Install & Verify Ollama LLM (Host)
```bash
# Install Ollama (Host)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the lightweight 1.5B parameter model
ollama pull qwen2.5:1.5b

# Verify Ollama service is active
systemctl is-active ollama
```

### 3. Download QGroundControl (Host)
```bash
# Download latest stable AppImage
wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage -O ~/QGroundControl.AppImage

# Make executable
chmod +x ~/QGroundControl.AppImage
```

### 4. Build / Launch Docker Container
The simulation runs inside a self-contained Docker container configured with ROS 2 Jazzy, PX4 SITL v1.15, and Gazebo Harmonic:

```bash
cd docker
chmod +x run.sh run_sim.sh
./run.sh
```
*`run.sh` automatically detects your NVIDIA GPU and passes `--gpus all`, discrete rendering flags, and local X11 display sockets.*

---

## 🚀 Step-by-Step Execution Guide

To understand the robotics pipeline mechanics, follow this 5-terminal workflow:

### **Terminal 1: Gazebo Harmonic + PX4 Drone Simulation**
In your host terminal, grant GUI access and enter the container:
```bash
# 1. Allow Docker container to access host X11 display
xhost +local:root

# 2. Attach to persistent container
docker start -ai drone_jazzy_sim_instance
```
Inside the container shell (`root@...:/workspace#`), launch PX4 SITL & Gazebo with NVIDIA PRIME GPU offload:
```bash
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export PX4_GZ_WORLD="drone_obstacle_world"
export PX4_SYS_AUTOSTART=4010
export PX4_SIM_MODEL="x500_mono_cam"
export GZ_CONFIG_PATH="/usr/share/gz${GZ_CONFIG_PATH:+:${GZ_CONFIG_PATH}}"

/opt/px4-gazebo/bin/px4-gazebo
```
*(Or simply run the automated script: `/workspace/docker/run_sim.sh`)*

* **`PX4_GZ_WORLD="drone_obstacle_world"`**: Loads custom world with human ($4\text{m}$), SUV ($6\text{m}$), and red cube ($3\text{m}$) obstacles.
* **`PX4_SYS_AUTOSTART=4010`**: PX4 airframe ID for `x500_mono_cam` (quadcopter with forward-mounted camera).
* **`__NV_PRIME_RENDER_OFFLOAD=1`**: Forces Gazebo Harmonic rendering to the dedicated NVIDIA GPU.

---

### **Terminal 2: Micro-XRCE-DDS Agent**
On the host machine, open a new terminal:
```bash
docker exec -it drone_jazzy_sim_instance bash -c "source /opt/ros/jazzy/setup.bash && MicroXRCEAgent udp4 -p 8888"
```
* Translates PX4 uORB messages to ROS 2 topics (`/fmu/in/*`, `/fmu/out/*`) over UDP port 8888.

---

### **Terminal 3: Onboard Camera Bridge & YOLOv8 Perception**
On the host machine, open a 3rd terminal:
```bash
docker exec -it drone_jazzy_sim_instance /workspace/scripts/start_vision.sh
```
* **Auto-Discovery:** `start_vision.sh` dynamically discovers the active Gazebo camera topic (e.g., `/world/drone_obstacle_world/model/x500_mono_cam_0/...`) and launches `ros_gz_bridge`.
* Launches Ultralytics YOLOv8 real-time detector on the `/camera/image_raw` feed.

---

### **Terminal 4: Web Ground Control Station (GCS)**
On the host machine, open a 4th terminal:
```bash
docker exec -it drone_jazzy_sim_instance bash -c "source /opt/ros/jazzy/setup.bash && source /opt/px4_ros2/install/setup.bash && python3 /workspace/scripts/web_ground_station.py 8080"
```
* Starts the interactive Web GCS dashboard on port 8080.
* Integrated with Ollama `"keep_alive": "60m"` to eliminate cold-start LLM latency.
* Timestamp query parameter (`?t=Date.now()`) guarantees immediate cache-busting for aerial camera snapshots.

---

### **Terminal 5: QGroundControl HUD (Host)**
On the host machine, launch QGroundControl with NVIDIA discrete GPU offload:
```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia ~/QGroundControl.AppImage
```
* Connects automatically to PX4 SITL MAVLink broadcast (`UDP 18570 / 14550`).
* Displays Artificial Horizon, Attitude tape, Altitude AGL, and GPS map at full 60fps.

---

## 🧪 Verification and Benchmark Suite

### 1. Browser Mission Scenarios
Open your browser at **`http://localhost:8080`**:

| Scenario | Natural Command (English / Bengali) | Expected Gatekeeper Behavior | Expected Drone Action |
| :--- | :--- | :--- | :--- |
| **Low-Altitude Collision** | `"সামনে ৫ মিটার যাও"` or `"Go forward 5m"` | **REJECTED 🛑** (`Detected 'BUS' ~3.7m ahead. Climb to >=3m`) | Motors remain idle; no flight hazard. |
| **Safe Altitude Climb** | `"Take off to 5 meters"` | **APPROVED ✅** | Spools up motors, climbs to $5.0\text{ m}$, hovers. |
| **High-Altitude Overflight** | `"Take off to 7 meters then go forward 10 meters"` | **APPROVED ✅** (`Overflight Safe: Cruising at 7m (+4m clearance)`) | Climbs to $7.0\text{ m}$, flies forward $10.0\text{ m}$ directly over the car/person. |
| **Aerial Photo Reconnaissance** | `"Take a photo"` or `"ছবি তোলো"` | **APPROVED ✅** | Triggers camera shutter, saves and displays fresh snapshot in UI with timestamp cache-busting. |

### 2. Automated 22/22 LLM & Safety Benchmark
Run the standalone regression test suite:
```bash
docker exec -it drone_jazzy_sim_instance bash -c "source /opt/ros/jazzy/setup.bash && python3 -m pytest /workspace/tests/benchmark_test_suite.py -v"
```
```text
============================== 22 passed in 1.48s ==============================
✅ 10/10 Natural Language Intent Tests (English & Bengali) Passed
✅ 12/12 3D Altitude-Aware Collision & Geofence Tests Passed
```

---

## 🛠️ Key Technical Challenges & Solutions

| Technical Challenge | Root Cause | Engineering Solution |
| :--- | :--- | :--- |
| **Simulation Stutter / CPU Pegged (100%)** | Gazebo, PX4 SITL, and YOLO were executing on software Intel UHD rendering. | Installed `nvidia-container-toolkit`, configured Docker `--gpus all`, and offloaded rendering via `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia`. |
| **Docker `could not select device driver ""`** | Docker daemon lacked NVIDIA runtime configuration. | Configured daemon via `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`. |
| **ASUS Laptop dGPU Missing (`NVRM`)** | Hardware WMI power switch `/sys/devices/platform/asus-nb-wmi/dgpu_disable` was active (`1`). | Toggled switch via `echo 0 | sudo tee .../dgpu_disable` and triggered a PCI bus rescan. |
| **Ollama Read Timeout on Cold Start** | Initial model load into VRAM took ~54s, exceeding 60s HTTP client timeout. | Added `"keep_alive": "60m"` in payload and increased client timeout to 90s. |
| **Stale Aerial Camera Snapshots in Web UI** | Browser HTTP cache served previous `/captures/latest.jpg` image. | Added timestamp cache-busting (`/captures/latest.jpg?t=${Date.now()}`) in `web_ground_station.py`. |
| **Camera Bridge Broken After Airframe Change** | Hardcoded topic string looked for `/world/.../gz_x500_0/...` instead of `x500_mono_cam_0`. | Enhanced `start_vision.sh` to auto-discover active Gazebo camera topics dynamically. |
| **Gazebo CLI `gz sim` Missing** | Sourcing ROS 2 Jazzy overwrote `GZ_CONFIG_PATH` with vendor paths, hiding `/usr/share/gz/sim8.yaml`. | Explicitly bound `/usr/share/gz` into `GZ_CONFIG_PATH` in `~/.bashrc` and launcher scripts. |
| **PX4 SITL Timed Out on Startup** | World name in SDF was `<world name="default">`, but PX4 searched for `/world/drone_obstacle_world/scene/info`. | Renamed world XML tag to `<world name="drone_obstacle_world">`. |
| **Preflight Check Failed (No Arm)** | Dedicated world SDF was missing Gazebo `AirPressure` (barometer) and `Magnetometer` (compass) plugins. | Added all 11 core Gazebo sensor plugins to `drone_obstacle_world.sdf`. |
| **Drone Propellers Spun but No Lift** | PX4 v1.15 publishes vehicle status on `/fmu/out/vehicle_status_v4`, while GCS subscribed to legacy `/vehicle_status`. | Updated subscription to `/fmu/out/vehicle_status_v4`, enabling immediate detection of `ARMED` state. |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

## 👨‍💻 Author

**Nasimul Khaled Sami**  
- GitHub: [@Nasim-Sami](https://github.com/Nasim-Sami)  
- Portfolio: [ROS2-Mini-Projects](https://github.com/Nasim-Sami/ROS2-Mini-Projects)  
- Specialization: Autonomous Aerial Robotics, ROS 2, Embedded Autopilots, AI Perception & LLM Control
