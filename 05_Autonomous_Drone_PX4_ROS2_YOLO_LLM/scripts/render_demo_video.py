#!/usr/bin/env python3
"""
Autonomous Drone Professional Demo Video Generator
--------------------------------------------------
Edits raw flight footage into a polished, high-impact portfolio video:
- Cuts out dead waiting time & removes last 15 seconds
- Retains all 5 core aerial robotics features with cinematic lower-third banners
- Sets speed to 1.18x (well within <=1.3x limit)
- Fits final duration strictly between 2.0 and 2.5 minutes (~2m 29s)
- Encodes with NVIDIA NVENC H.264 for high compression and crystal-clear 1080p 60fps quality
- NO emojis or icons on screen (clean professional ASCII typography)
"""

import sys
import os
import cv2
import numpy as np
import subprocess

INPUT_PATH = "/workspace/raw_video.mp4"
OUTPUT_PATH = "/workspace/Autonomous_Drone_PX4_ROS2_YOLO_LLM_Demo.mp4"
SPEED_FACTOR = 1.18
OUT_FPS = 60.0
W, H = 1920, 1080

# Define 5 high-impact feature segments (times in seconds)
SEGMENTS = [
    {
        "name": "LLM Mission Planning & Takeoff",
        "ranges": [(18.0, 46.0)], # 28s
        "tag": "FEATURE 01",
        "title": "Natural Language Mission Planning & Autonomous Takeoff",
        "subtitle": "Small LLM (Qwen 2.5 1.5B) Intent Decomposition -> 3D Safety Gatekeeper -> PX4 Offboard Mode"
    },
    {
        "name": "Circular Orbit & QGroundControl Sync",
        "ranges": [(58.0, 95.0)], # 37s
        "tag": "FEATURE 02",
        "title": "4m Circular Orbit Trajectory & QGroundControl HUD Sync",
        "subtitle": "Real-time Heading, Compass & Attitude Tracking on QGroundControl HUD & Map"
    },
    {
        "name": "YOLOv8 Aerial Perception & Photo Capture",
        "ranges": [(165.0, 198.0)], # 33s
        "tag": "FEATURE 03",
        "title": "YOLOv8 Aerial Perception & Camera Snapshot Capture",
        "subtitle": "Altitude Climb to 15m | Real-Time Obstacle Detection & Live Camera Frame Acquisition"
    },
    {
        "name": "Dynamic 3D Trajectory Tracking",
        "ranges": [(215.0, 238.0), (260.0, 285.0)], # 23s + 25s = 48s
        "tag": "FEATURE 04",
        "title": "Dynamic 3D Trajectory Tracking (Zigzag & Spiral Ascend)",
        "subtitle": "High-Performance Parametric Trajectory Generator | EKF2 Altitude Stabilization"
    },
    {
        "name": "Autonomous Return & Precision Landing",
        "ranges": [(422.0, 452.0)], # 30s (ends before last 15s)
        "tag": "FEATURE 05",
        "title": "Autonomous Safe Landing & Mission Complete",
        "subtitle": "Safe Vertical Descent Trajectory -> Smooth Touchdown & Motor Disarming"
    }
]

def draw_banner(frame, tag, title, subtitle):
    overlay = frame.copy()
    bx1, by1 = 40, 950
    bx2, by2 = 1880, 1055
    
    # Dark slate background box
    cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (15, 23, 42), -1)
    
    # Cyan accent top line (3px)
    cv2.line(overlay, (bx1, by1), (bx2, by1), (255, 240, 0), 3) # BGR: Cyan #00f0ff
    
    # Alpha blend banner (88% opacity)
    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
    
    # Badge Pill: [FEATURE 0X] (Clean, strictly no emojis)
    pw, ph = 160, 36
    px1, py1 = bx1 + 25, by1 + 18
    px2, py2 = px1 + pw, py1 + ph
    cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 240, 0), -1)
    cv2.putText(frame, tag, (px1 + 14, py1 + 25), cv2.FONT_HERSHEY_DUPLEX, 0.65, (10, 15, 30), 2, cv2.LINE_AA)
    
    # Title (Crisp white text)
    cv2.putText(frame, title, (px2 + 25, py1 + 27), cv2.FONT_HERSHEY_DUPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Subtitle (Light slate text)
    cv2.putText(frame, subtitle, (bx1 + 25, by2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (200, 215, 230), 1, cv2.LINE_AA)

def main():
    if not os.path.exists(INPUT_PATH):
        print(f"Error: Input video not found at {INPUT_PATH}")
        sys.exit(1)

    cap = cv2.VideoCapture(INPUT_PATH)
    in_fps = cap.get(cv2.CAP_PROP_FPS) or 60.0
    print(f"Loaded input video: {W}x{H} @ {in_fps:.1f} FPS")

    # Launch FFmpeg NVENC process
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "bgr24",
        "-r", str(OUT_FPS),
        "-i", "-",
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-cq", "23",
        "-b:v", "4500k",
        "-maxrate", "6000k",
        "-bufsize", "10000k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        OUTPUT_PATH
    ]
    
    print(f"Starting FFmpeg encoder with NVENC...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    total_frames_written = 0

    for seg_idx, seg in enumerate(SEGMENTS):
        print(f"\nProcessing [{seg['tag']}]: {seg['name']}...")
        tag = seg["tag"]
        title = seg["title"]
        subtitle = seg["subtitle"]

        for r_start, r_end in seg["ranges"]:
            start_frame = int(r_start * in_fps)
            end_frame = int(r_end * in_fps)
            
            # Seek ONCE to segment start
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # Sequential reading with float accumulator for speed factor
            accumulator = 0.0
            for curr_frame_idx in range(start_frame, end_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                
                accumulator += 1.0
                if accumulator >= SPEED_FACTOR:
                    accumulator -= SPEED_FACTOR
                    
                    # Overlay lower-third banner (strictly no emojis)
                    draw_banner(frame, tag, title, subtitle)
                    
                    # Stream to FFmpeg
                    proc.stdin.write(frame.tobytes())
                    total_frames_written += 1

    cap.release()
    proc.stdin.close()
    proc.wait()

    final_dur = total_frames_written / OUT_FPS
    final_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024) if os.path.exists(OUTPUT_PATH) else 0.0

    print(f"\n=======================================================")
    print(f"🎉 Rendering Complete!")
    print(f"📹 Output Video: {OUTPUT_PATH}")
    print(f"⏱️ Final Duration: {final_dur:.2f}s ({final_dur/60:.2f} min)")
    print(f"📦 Final File Size: {final_size_mb:.2f} MB")
    print(f"⚡ Speed Factor Applied: {SPEED_FACTOR}x (Strictly <= 1.3x)")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
