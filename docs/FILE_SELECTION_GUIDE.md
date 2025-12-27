# 📸 File Selection Guide

This guide explains how to use the **file selection** feature to analyze uploaded images and videos.

---

## 🚀 Quick Start

### Method 1: Interactive Launcher (Easiest)

```bash
python launch.py
```

You'll see a menu:
```
==========================================================
🚆 RAILTRACK - Railway Obstacle Detection System
==========================================================

Choose input mode:
  1. Live Camera Processing
  2. Process Single Image
  3. Process Video File
  4. Auto-detect Media File
  5. Exit

Enter your choice (1-5):
```

**Options:**
- **Option 1**: Uses your webcam for real-time detection
- **Option 2**: Upload a single image (JPG, PNG, BMP, TIFF)
- **Option 3**: Upload a video file (MP4, AVI, MOV, MKV, etc.)
- **Option 4**: Automatically detects if file is image or video
- **Option 5**: Exit the application

---

## 📋 Detailed Usage

### Option 2: Process Single Image

1. Run `python launch.py`
2. Select option **2**
3. A file dialog will open
4. Select an image file (supported: jpg, jpeg, png, bmp, tiff)
5. The system will:
   - Load the image
   - Detect railway tracks
   - Identify obstacles
   - Classify risk zones
   - Calculate severity
   - Display annotated result

**Example Output:**
```
Processing image: E:\RailTrack\test_images\railway_track.jpg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DETECTION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Obstacles: 2

Obstacle #1:
  Type: person
  Confidence: 0.89
  Location: (245, 156) - (389, 412)
  Track Zone: critical_zone
  Collision Risk: HIGH

Obstacle #2:
  Type: car
  Confidence: 0.76
  Location: (512, 234) - (698, 445)
  Track Zone: warning_zone
  Collision Risk: MEDIUM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ SEVERITY ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity: CRITICAL
Reason: Human detected in critical zone

Actions Required:
  - IMMEDIATE EMERGENCY BRAKE
  - Alert control room
  - Activate all warning systems

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press any key to close (press 's' to save result)...
```

**Keyboard Controls:**
- **Any key**: Close and return to menu
- **s**: Save annotated image to `data/processed/` directory

---

### Option 3: Process Video File

1. Run `python launch.py`
2. Select option **3**
3. A file dialog will open
4. Select a video file (supported: mp4, avi, mov, mkv, flv, wmv)
5. The system will:
   - Process each frame
   - Track obstacles across frames
   - Show real-time visualization
   - Log all detections

**Video Processing Features:**
- **Multi-frame confirmation**: Reduces false alerts
- **Temporal tracking**: Tracks same obstacle across frames
- **Time-to-Collision**: Estimates TTC for moving obstacles
- **Progress indicator**: Shows processing progress

**Example:**
```
Processing video: E:\RailTrack\videos\train_footage.mp4

Frame: 245/1850 (13.2%)
FPS: 28.5
Obstacles detected: 1
Current severity: MEDIUM

[Press 'q' to stop, 's' to screenshot]
```

**Keyboard Controls:**
- **q**: Stop processing and return to menu
- **s**: Save current frame screenshot
- **r**: Print current report

---

### Option 4: Auto-detect Media File

1. Run `python launch.py`
2. Select option **4**
3. A file dialog will open
4. Select **any** image or video file
5. The system **automatically detects** the type and processes accordingly

This is useful when you have mixed media files and don't want to select the option manually.

---

## 🖼️ Supported File Formats

### Images
- **JPG/JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **BMP** (.bmp)
- **TIFF** (.tiff, .tif)

### Videos
- **MP4** (.mp4)
- **AVI** (.avi)
- **MOV** (.mov)
- **MKV** (.mkv)
- **FLV** (.flv)
- **WMV** (.wmv)

---

## 🎨 Visualization Elements

When viewing results, you'll see:

1. **Track Zones** (color-coded):
   - 🔴 **Red Zone**: Critical (immediate danger)
   - 🟡 **Yellow Zone**: Warning (potential hazard)
   - 🟢 **Green Zone**: Safe (monitored area)

2. **Detection Boxes**:
   - Bounding boxes around detected objects
   - Labels showing object type and confidence
   - Different colors for different risk levels

3. **Status Information**:
   - Frame number / Total frames (for videos)
   - FPS (frames per second)
   - Number of obstacles detected
   - Current severity level

---

## 💡 Tips and Best Practices

### For Best Results:

1. **Image Quality**:
   - Use high-resolution images (minimum 640x480)
   - Ensure good lighting (or use night vision mode)
   - Avoid heavily compressed or blurry images

2. **Camera Angle**:
   - Forward-facing view works best
   - Track should be clearly visible
   - Avoid extreme angles

3. **Video Files**:
   - Higher frame rates (30+ FPS) improve tracking
   - Stable camera mounting reduces false detections
   - MP4 format recommended for compatibility

4. **File Organization**:
   ```
   RailTrack/
   ├── test_images/       # Place test images here
   ├── test_videos/       # Place test videos here
   └── data/
       ├── processed/     # Saved results appear here
       └── logs/          # Detection logs stored here
   ```

---

## 🔧 Troubleshooting

### "No file selected" Error
- **Cause**: File dialog was cancelled
- **Solution**: Try again and select a valid file

### "Unsupported file format" Error
- **Cause**: File type not supported
- **Solution**: Convert to supported format (JPG, PNG, MP4, etc.)

### "Failed to load file" Error
- **Cause**: File is corrupted or path contains special characters
- **Solution**: 
  - Verify file is not corrupted
  - Move file to path without special characters
  - Try a different file

### Processing is Very Slow
- **Cause**: Large file or CPU processing
- **Solutions**:
  - Use GPU acceleration (configure CUDA)
  - Reduce video resolution
  - Use smaller YOLO model (yolov8n.pt)

### No Tracks Detected
- **Cause**: Track not visible or poor quality
- **Solutions**:
  - Ensure railway tracks are clearly visible
  - Improve image quality/lighting
  - Adjust track detection thresholds in config

---

## 🎯 Example Workflows

### Workflow 1: Test with Sample Image

```bash
# 1. Download or capture a railway track image
# 2. Run launcher
python launch.py

# 3. Select option 2 (Process Single Image)
# 4. Browse to your image
# 5. View results
# 6. Press 's' to save if needed
# 7. Return to menu and try another image
```

### Workflow 2: Analyze Recorded Video

```bash
# 1. Have a video file ready (e.g., dashcam footage)
# 2. Run launcher
python launch.py

# 3. Select option 3 (Process Video File)
# 4. Browse to your video
# 5. Watch real-time processing
# 6. Press 's' to save interesting frames
# 7. Check logs/ directory for detailed results
```

### Workflow 3: Batch Processing Multiple Files

```bash
# 1. Prepare multiple images/videos
# 2. Run launcher
python launch.py

# 3. Select option 4 (Auto-detect)
# 4. Process first file
# 5. After completion, menu appears again
# 6. Select option 4 again for next file
# 7. Repeat until all files processed
# 8. Select option 5 to exit
```

---

## 📊 Output Files

### Processed Images
Saved to: `data/processed/result_YYYYMMDD_HHMMSS.jpg`

Contains:
- Original image with annotations
- Detection bounding boxes
- Track zone overlays
- Risk level indicators

### Log Files
Saved to: `logs/incidents_YYYYMMDD.json` and `logs/railtrack.log`

Contains:
- Timestamp of detection
- File name and path
- All detected obstacles
- Risk assessments
- Severity classifications

---

## 🚀 Advanced: Programmatic Usage

You can also use the modules directly in your own scripts:

```python
from src.file_selector import FileSelector
from src.image_processor import ImageProcessor

# Initialize
selector = FileSelector()
processor = ImageProcessor()

# Select and process image
image_path = selector.select_file(
    title="Select Railway Image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

if image_path:
    results = processor.process_image(image_path, show_result=True)
    print(f"Detected {len(results['obstacles'])} obstacles")
```

---

## 📞 Need Help?

- Check [README.md](README.md) for general system information
- See [QUICKSTART.md](docs/QUICKSTART.md) for installation help
- Review [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) for architecture details

---

**Happy Testing! 🚆🔍**
