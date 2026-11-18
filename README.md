# 🚁 Autonomous Aerial Robotics: PX4 SITL + ROS 2 Jazzy + Gazebo Harmonic + YOLOv8 + Small LLM

<div align="center">

[![ROS 2](https://img.shields.io/badge/ROS_2-Jazzy_Jalisco-22314E?style=for-the-badge&logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/)
[![PX4 Autopilot](https://img.shields.io/badge/PX4_Autopilot-v1.15_SITL-EE3322?style=for-the-badge&logo=drone&logoColor=white)](https://px4.io/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic_8.15-FF6600?style=for-the-badge&logo=gazebo&logoColor=white)](https://gazebosim.org/)
[![QGroundControl](https://img.shields.io/badge/QGroundControl-v4.4_MAVLink-007ACC?style=for-the-badge&logo=gnome-terminal&logoColor=white)](http://qgroundcontrol.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5_1.5B-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8_Nano-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![GitHub Profile](https://img.shields.io/badge/Developer-Nasim--Sami-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nasim-Sami)

**A complete, production-grade autonomous quadcopter pipeline featuring Natural Language Mission Planning (English & Bengali), Physics-Based 3D Trajectory Gatekeeper, Real-time YOLOv8 Computer Vision Perception, and PX4 SITL Offboard Flight Control.**

[Overview](#-overview) • [Architecture](#-architecture) • [Project Structure](#-project-structure) • [Quick Start](#-quick-start) • [Detailed Documentation](#-detailed-project-guide) • [Author](#-author)

</div>

---

## 📖 Overview

This repository houses an end-to-end autonomous drone navigation, perception, and mission planning system. The quadcopter operates in **PX4 SITL v1.15** with high-fidelity physics in **Gazebo Harmonic**, accepting spoken or typed instructions in **English** and **Bengali** through an interactive Web Ground Control Station.

### Core Capabilities:
- **Natural Language Mission Planning**: Decomposes natural language commands into structured flight primitives using an on-device Small Language Model (**Ollama `qwen2.5:1.5b`**).
- **Physics-Based 3D Safety Gatekeeper**: Evaluates kinematic feasibility, a $300\text{ m}$ radius geofence, a $150\text{ m}$ ceiling, and dynamic overflight clearance against obstacles.
- **Onboard Neural Vision Perception**: Ultralytics **YOLOv8 Nano** runs real-time inference on the drone's forward camera, detecting humans, vehicles, and obstacles in the flight path and capturing dynamic reconnaissance snapshots.
- **Deterministic 10Hz Offboard Trajectory Tracking**: Generates smooth parametric 3D waypoints in PX4 NED frame and streams setpoints via Micro-XRCE-DDS.
- **Dual Telemetry Monitoring**: Streams real-time flight telemetry to both a custom Web GCS dashboard and **QGroundControl** (Artificial Horizon, HUD, and 3D satellite map).

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph UI ["Operator Control & Monitoring"]
        WebGCS["Web Ground Control Station (Port 8080)<br/>Bilingual Voice / Text • Live Telemetry & Snapshots"]
        QGC["QGroundControl (MAVLink UDP 18570)<br/>Artificial Horizon • Altitude Tape • Satellite Map"]
    end

    subgraph Intelligence ["AI Reasoning & Safety Filter"]
        LLM["Ollama Small LLM (qwen2.5:1.5b)<br/>Speech/Text Intent Decomposition"]
        Gatekeeper["3D Altitude-Aware Trajectory Gatekeeper<br/>Collision Avoidance • 10x Safety Boundaries"]
        Trajectory["10Hz NED Trajectory Generator<br/>Parametric 3D Waypoint Streamer"]
    end

    subgraph Perception ["Vision & Perception Pipeline"]
        GZCam["Gazebo Onboard Mono Camera<br/>x500_mono_cam (Airframe 4010)"]
        Bridge["ros_gz_bridge<br/>GZ Image ➔ ROS 2 /camera/image_raw"]
        YOLO["Ultralytics YOLOv8 Nano<br/>Real-Time Detection & Proximity Estimation"]
    end

    subgraph Autopilot ["Flight Execution & Simulation"]
        ROS2Node["ROS 2 Jazzy Jalisco<br/>GCSBridgeNode • Offboard Publisher"]
        XRCE["Micro-XRCE-DDS Agent<br/>UDP 8888 Bridge"]
        PX4["PX4 SITL v1.15 Autopilot<br/>Offboard Mode • EKF2 State Estimator"]
        Gazebo["Gazebo Harmonic 8.15 Physics<br/>drone_obstacle_world.sdf"]
    end

    WebGCS -->|Voice / Text Command| LLM
    LLM -->|Structured Steps| Gatekeeper
    GZCam --> Bridge --> YOLO
    YOLO -->|Obstacle Threat & Distance| Gatekeeper
    Gatekeeper -->|Approved Mission| Trajectory
    Trajectory -->|10Hz Setpoints| ROS2Node
    ROS2Node <==>|uORB Topics / DDS| XRCE <==> PX4
    PX4 <==>|gz-sim Sensor Systems| Gazebo
    PX4 -.->|MAVLink Telemetry| QGC
    ROS2Node -->|Telemetry & Snapshots| WebGCS
```

---

## 📁 Project Structure

```text
Autonomous-Drone-PX4-ROS2-YOLO-LLM/
├── README.md                                          # Root repository overview & architecture
├── LICENSE                                            # MIT License
├── .gitignore                                         # Git ignore rules
│
└── 05_Autonomous_Drone_PX4_ROS2_YOLO_LLM/             # Core Project Directory
    ├── README.md                                      # Comprehensive guide: installation, execution & troubleshooting
    ├── requirements.txt                               # Python dependencies (YOLO, OpenCV, Ollama, etc.)
    ├── yolov8n.pt                                     # Pre-trained YOLOv8 Nano neural network weights
    │
    ├── docker/                                        # Containerized Simulation Environment
    │   ├── Dockerfile                                 # Multi-stage Ubuntu 24.04 + ROS 2 Jazzy + PX4 + Gazebo
    │   ├── run.sh                                     # Persistent container runner with GPU & X11 display
    │   ├── run_sim.sh                                 # One-click PX4 SITL + Gazebo launcher
    │   └── drone_obstacle_world.sdf                   # Custom world with human, car, and cube obstacles
    │
    ├── scripts/                                       # ROS 2 Nodes & AI Pipeline
    │   ├── web_ground_station.py                      # Interactive Web GCS dashboard on port 8080
    │   ├── drone_intent_parser.py                     # Ollama natural language mission parser (EN & BN)
    │   ├── drone_safety_validator.py                  # 3D Altitude-Aware Trajectory Gatekeeper
    │   ├── trajectory_generator.py                    # 10Hz parametric waypoint streamer (NED frame)
    │   ├── drone_vision_detector.py                   # Real-time YOLOv8 detector & snapshot saver
    │   ├── start_vision.sh                            # Camera parameter bridge & YOLO launcher
    │   ├── autonomous_llm_flight_node.py              # Standalone interactive CLI node
    │   └── offboard_drone_commander.py                # Reference offboard commander
    │
    ├── tests/                                         # Regression Benchmark Suite
    │   └── benchmark_test_suite.py                    # 22/22 Benchmark test suite (EN & BN intent + safety)
    │
    └── captures/                                      # Aerial reconnaissance snapshots directory
        └── latest.jpg                                 # Live snapshot served to Web UI
```

---

## ⚡ Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/Nasim-Sami/Autonomous-Drone-PX4-ROS2-YOLO-LLM.git
cd Autonomous-Drone-PX4-ROS2-YOLO-LLM/05_Autonomous_Drone_PX4_ROS2_YOLO_LLM

# 2. Start the simulation container
cd docker && ./run.sh

# 3. Inside the container shell, launch PX4 SITL & Gazebo:
/workspace/docker/run_sim.sh
```

In separate host terminals, launch the bridge, vision perception, and web control station:
```bash
# Terminal 2: Micro-XRCE-DDS Agent
docker exec -it drone_jazzy_sim_instance bash -c "source /opt/ros/jazzy/setup.bash && MicroXRCEAgent udp4 -p 8888"

# Terminal 3: Camera Bridge & YOLOv8
docker exec -it drone_jazzy_sim_instance /workspace/scripts/start_vision.sh

# Terminal 4: Web Ground Station
docker exec -it drone_jazzy_sim_instance bash -c "source /opt/ros/jazzy/setup.bash && source /opt/px4_ros2/install/setup.bash && python3 /workspace/scripts/web_ground_station.py 8080"
```

Open **`http://localhost:8080`** in your browser, speak or type your mission, and watch the drone navigate autonomously!

---

## 📖 Detailed Project Guide

For an in-depth walkthrough—including detailed software prerequisites, raw terminal commands without helper scripts, 3D overflight logic, benchmark results, and an exhaustive troubleshooting matrix:

👉 **Read the full [Project 05 Documentation](05_Autonomous_Drone_PX4_ROS2_YOLO_LLM/README.md).**

---

## 📄 License

This repository is distributed under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Nasimul Khaled Sami**  
- **GitHub**: [@Nasim-Sami](https://github.com/Nasim-Sami)  
- **Portfolio Repository**: [ROS2-Mini-Projects](https://github.com/Nasim-Sami/ROS2-Mini-Projects)  
- **Domain**: Autonomous Aerial Robotics, Autonomous Mobile Robots (AMR), Computer Vision, Embedded Autopilots & LLM Ground Stations
