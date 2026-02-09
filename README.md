# Iron Man Style Hand Tracking HUD

Real-time hand gesture controlled 3D interaction system inspired by Iron Man HUDs.

## Features
- Real-time hand tracking (MediaPipe)
- Stable pinch detection
- 3D translation, rotation, and zoom
- UDP-based Python → Unity communication
- Interactive Iron-Man style HUD

## Tech Stack
- Python (OpenCV, MediaPipe)
- Unity 6 (URP)
- UDP networking

## How It Works
1. Python tracks hand landmarks via webcam
2. Gesture logic extracts position, rotation, zoom
3. Data streamed via UDP to Unity
4. Unity applies real-time 6DOF control
5. HUD reacts live to gestures



## Future Improvements
- Multi-hand support
- Object switching
- AR headset integration
