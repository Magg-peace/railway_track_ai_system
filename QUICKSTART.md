# RailTrack Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install

```bash
# Clone or download the repository
cd RailTrack

# Run setup script
python setup.py
```

### Step 2: Configure

Edit `config/config.yaml`:

```yaml
camera:
  source: 0  # Use 0 for webcam, or path to video file

alerts:
  telegram:
    enabled: false  # Set to true if you have Telegram bot
```

### Step 3: Run

```bash
python main.py
```

That's it! The system should now be running.

---

## 📹 Video Source Options

### Use Webcam
```yaml
camera:
  source: 0
```

### Use Video File
```yaml
camera:
  source: "path/to/video.mp4"
```

### Use IP Camera (RTSP)
```yaml
camera:
  source: "rtsp://username:password@ip_address:port/stream"
```

---

## 🔔 Setting Up Alerts

### Telegram Bot Setup

1. **Create Bot**:
   - Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot`
   - Follow instructions
   - Copy the bot token

2. **Get Chat ID**:
   - Talk to [@userinfobot](https://t.me/userinfobot)
   - Copy your chat ID

3. **Configure**:
```yaml
alerts:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_ids:
      - "YOUR_CHAT_ID"
```

---

## 🎮 Keyboard Controls

While the system is running:

- **Q** - Quit the application
- **S** - Save screenshot of current frame
- **R** - Print system report to console

---

## ⚙️ Common Configuration Changes

### Adjust Detection Sensitivity

```yaml
yolo:
  confidence_threshold: 0.5  # Lower = more detections, more false positives
                             # Higher = fewer detections, fewer false positives
```

### Change Alert Thresholds

```yaml
distance:
  ttc_critical: 20  # Seconds for critical alert
  ttc_high: 40      # Seconds for high alert
  ttc_medium: 60    # Seconds for medium alert
```

### Adjust Track Zones

```yaml
track:
  left_rail_x: 0.35    # Left boundary (0-1)
  right_rail_x: 0.65   # Right boundary (0-1)
  track_top_y: 0.4     # Top boundary (0-1)
  track_bottom_y: 0.95 # Bottom boundary (0-1)
```

---

## 🐛 Troubleshooting

### Camera Not Working

**Problem**: "Could not open video source"

**Solutions**:
1. Check camera index (try 0, 1, 2)
2. Verify camera permissions
3. Test with video file instead

### Slow Performance

**Problem**: Low FPS

**Solutions**:
1. Enable GPU:
   ```yaml
   yolo:
     device: "cuda"
   ```
2. Lower resolution:
   ```yaml
   video:
     resize_width: 416
     resize_height: 416
   ```
3. Skip frames:
   ```yaml
   video:
     frame_skip: 2  # Process every 2nd frame
   ```

### CUDA Errors

**Problem**: "CUDA out of memory"

**Solutions**:
1. Use CPU mode:
   ```yaml
   yolo:
     device: "cpu"
   ```
2. Use smaller model:
   ```yaml
   yolo:
     model_path: "models/yolov8n.pt"  # Nano model
   ```

### No Detections

**Problem**: System doesn't detect obstacles

**Solutions**:
1. Lower confidence threshold:
   ```yaml
   yolo:
     confidence_threshold: 0.3
   ```
2. Check track zone configuration
3. Verify camera view shows track clearly

---

## 📊 Viewing Logs

### Incident Logs

JSON format logs:
```
logs/incidents/incidents_YYYYMMDD.json
```

### Alert Logs

```
logs/alerts.json
```

### Database

SQLite database:
```
logs/railtrack.db
```

Query using:
```bash
sqlite3 logs/railtrack.db "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🔧 Advanced Usage

### Custom Model Training

1. Prepare dataset in YOLO format
2. Place in `data/` directory
3. Train:
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8n.pt')
   model.train(data='data/dataset.yaml', epochs=100)
   ```

### API Integration

Coming soon: REST API for integration with other systems

### Multi-Camera Setup

Coming soon: Support for multiple cameras

---

## 📞 Getting Help

1. Check [README.md](README.md) for detailed documentation
2. Review configuration in `config/config.yaml`
3. Check logs in `logs/` directory
4. Create an issue on GitHub

---

## 🎯 Next Steps

1. ✅ Get system running
2. ⚙️ Adjust configuration for your setup
3. 🧪 Test with sample videos
4. 🔔 Set up alerts
5. 📊 Review analytics
6. 🚂 Deploy on real system

---

**Happy Railway Safety Monitoring! 🚆**
