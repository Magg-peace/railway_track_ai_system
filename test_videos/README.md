# Test Videos

Place your test railway track videos here for analysis.

## Supported Formats
- MP4 (.mp4) - **Recommended**
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)

## How to Use

1. Copy or download railway track videos to this directory
2. Run: `python launch.py`
3. Select option **3** (Process Video File)
4. Browse and select a video from this folder
5. Watch real-time processing with detection overlay

## Sample Videos

You can obtain sample railway footage from:
- YouTube (train cab view videos)
- Railway datasets (Kaggle, UCI ML Repository)
- Dashboard cameras / action cameras
- Drone footage of railway tracks

## Best Video Characteristics

For optimal detection results:
- **Resolution**: Minimum 640x480, recommended 1920x1080
- **Frame Rate**: 30 FPS or higher
- **Angle**: Forward-facing view from train or beside tracks
- **Stability**: Steady camera, avoid excessive shaking
- **Duration**: Any length (system processes frame-by-frame)
- **Format**: MP4 with H.264 codec for best compatibility

## Video Processing Features

The system provides:
- **Multi-frame confirmation**: Tracks obstacles across frames to reduce false alerts
- **Temporal tracking**: Follows same obstacle through video
- **Time-to-Collision**: Estimates TTC for moving objects
- **Real-time visualization**: See detections as video plays
- **Progress indicator**: Monitor processing progress
- **Screenshot capture**: Press 's' to save interesting frames

## Keyboard Controls While Processing

- **q** - Stop processing and return to menu
- **s** - Save current frame as screenshot
- **r** - Print detection report for current frame

## Example File Structure

```
test_videos/
├── train_forward_view.mp4
├── track_with_obstacles.avi
├── night_railway.mp4
├── curved_track_section.mkv
└── station_approach.mp4
```

## Performance Tips

- **Large videos**: Processing may take time depending on length and resolution
- **GPU acceleration**: Enable CUDA for faster processing (see config.yaml)
- **Lower resolution**: For faster testing, use 720p instead of 1080p
- **Short clips**: Use 10-30 second clips for quick testing

## Output

Processed results are saved to:
- **Screenshots**: `data/processed/screenshot_TIMESTAMP.jpg`
- **Logs**: `logs/incidents_DATE.json` and `logs/railtrack.log`
- **Reports**: Console output with frame-by-frame statistics

## Notes

- Video processing uses the same detection pipeline as live camera
- All detection settings in `config/config.yaml` apply to video processing
- Videos are processed frame-by-frame (not real-time playback speed)
- Processing speed depends on: video resolution, frame rate, CPU/GPU, YOLO model size
