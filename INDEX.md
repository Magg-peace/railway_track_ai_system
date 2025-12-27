# 🚆 RailTrack - Navigation & Documentation Index

Welcome to the **RailTrack AI-Based Intelligent Railway Track Obstacle Detection & Collision Prevention System**!

---

## 📚 Documentation Navigation

### 🚀 Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide (START HERE!)
- **[README.md](README.md)** - Complete project documentation
- **[OVERVIEW.md](OVERVIEW.md)** - System architecture & flow diagrams
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project status & deliverables

### 📖 For Users
- **[QUICKSTART.md](QUICKSTART.md)** - Quick installation & first run
- **[FILE_SELECTION_GUIDE.md](docs/FILE_SELECTION_GUIDE.md)** - Upload & process images/videos 🆕
- **Configuration Guide** - See [config/config.yaml](config/config.yaml)
- **Usage Examples** - Run `python examples.py`
- **Troubleshooting** - See [QUICKSTART.md](QUICKSTART.md#troubleshooting)

### 👨‍💻 For Developers
- **[README.md](README.md#project-structure)** - Project structure
- **[OVERVIEW.md](OVERVIEW.md#system-flow-diagram)** - System architecture
- **Module Documentation** - Inline docs in `src/*.py`
- **API Reference** - See individual module files

### 🔧 Setup & Installation
1. **[setup.py](setup.py)** - Automated installation script
2. **[verify.py](verify.py)** - System verification
3. **[requirements.txt](requirements.txt)** - Dependencies list

---

## 📂 File Organization

### Core Application Files
```
main.py              → Main application entry point
launch.py            → Interactive file selection launcher 🆕
setup.py            → Installation & setup script
verify.py           → System verification
examples.py         → Usage examples & demos
```

### Documentation
```
README.md                  → Complete documentation
QUICKSTART.md              → 5-minute quick start
FILE_SELECTION_GUIDE.md    → Upload images/videos guide 🆕
OVERVIEW.md                → System architecture
PROJECT_SUMMARY.md         → Project status
INDEX.md                   → This file
```

### Source Code (`src/`)
```
video_capture.py              → Video input & preprocessing
track_segmentation.py         → Railway track detection
obstacle_detection.py         → YOLOv8 obstacle detection
multi_frame_confirmation.py   → False alert reduction
distance_ttc.py              → Distance & TTC calculation
severity_classification.py    → Severity assessment
alert_system.py              → Alert management
incident_logging.py          → Database & analytics
file_selector.py             → File selection dialog 🆕
image_processor.py           → Single image analysis 🆕
```

### Configuration (`config/`)
```
config.yaml         → Main system configuration (YAML)
```

### Utilities (`utils/`)
```
helpers.py          → Utility functions & helpers
```

---

## 🎯 Quick Links by Task

### "I want to..."

#### Install the system
→ Run `python setup.py` or see [QUICKSTART.md](QUICKSTART.md)

#### Run the system
→ Run `python launch.py` (interactive menu) or `python main.py` (direct camera)
See [FILE_SELECTION_GUIDE.md](docs/FILE_SELECTION_GUIDE.md) 🆕

#### Process images/videos
→ Run `python launch.py` and select option 2 or 3
See [FILE_SELECTION_GUIDE.md](docs/FILE_SELECTION_GUIDE.md) 🆕

#### Configure settings
→ Edit [config/config.yaml](config/config.yaml)

#### Set up alerts
→ See [QUICKSTART.md](QUICKSTART.md#setting-up-alerts)

#### View examples
→ Run `python examples.py`

#### Understand the system
→ Read [OVERVIEW.md](OVERVIEW.md)

#### Check installation
→ Run `python verify.py`

#### Troubleshoot issues
→ See [QUICKSTART.md](QUICKSTART.md#troubleshooting)

#### Deploy on Jetson Nano
→ See [README.md](README.md#deployment-options)

#### Contribute code
→ See [README.md](README.md#contributing)

---

## 📋 Module Descriptions

### 1. Video Capture (`video_capture.py`)
**Purpose**: Capture and preprocess video input
- Multi-source support (camera, file, RTSP)
- Low-light enhancement
- Frame denoising
- Frame buffering

### 2. Track Segmentation (`track_segmentation.py`)
**Purpose**: Detect and classify railway track zones
- Track region detection
- Zone classification (Critical/Warning/Safe)
- ROI management
- Visualization overlays

### 3. Obstacle Detection (`obstacle_detection.py`)
**Purpose**: Detect obstacles using YOLOv8
- Multi-class detection (human, animal, vehicle, debris)
- Object tracking
- Confidence filtering
- Bounding box visualization

### 4. Multi-Frame Confirmation (`multi_frame_confirmation.py`)
**Purpose**: Reduce false alerts through temporal verification
- Cross-frame tracking
- Persistence verification
- Static object detection
- False positive filtering

### 5. Distance & TTC (`distance_ttc.py`)
**Purpose**: Estimate distance and predict collision time
- Camera-based distance estimation
- Time-to-collision calculation
- Collision risk assessment
- Calibration support

### 6. Severity Classification (`severity_classification.py`)
**Purpose**: Classify incident severity and generate reports
- Rule-based severity engine
- Explainable AI reports
- Recommended action generation
- Incident summarization

### 7. Alert System (`alert_system.py`)
**Purpose**: Manage multi-channel alerts
- Telegram bot integration
- SMS support (Twilio)
- Local alerts (sound + display)
- Alert escalation
- Duplicate prevention

### 8. Incident Logging (`incident_logging.py`)
**Purpose**: Store and analyze incident data
- SQLite/MongoDB support
- JSON logging
- Analytics engine
- High-risk location identification
- Report generation

---

## 🔧 Configuration Reference

### Key Configuration Sections

| Section | Purpose | File |
|---------|---------|------|
| `camera` | Camera settings | config.yaml |
| `video` | Video processing | config.yaml |
| `yolo` | Detection model | config.yaml |
| `track` | Track zones | config.yaml |
| `confirmation` | Alert filtering | config.yaml |
| `distance` | Distance/TTC | config.yaml |
| `severity` | Classification rules | config.yaml |
| `alerts` | Alert channels | config.yaml |
| `logging` | Database settings | config.yaml |

---

## 🎓 Learning Path

### Beginner (New Users)
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run `python setup.py`
3. Run `python main.py`
4. Try `python examples.py`

### Intermediate (Customization)
1. Read [README.md](README.md)
2. Review [config/config.yaml](config/config.yaml)
3. Read [OVERVIEW.md](OVERVIEW.md)
4. Modify configuration settings

### Advanced (Development)
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Study module source code in `src/`
3. Review system architecture in [OVERVIEW.md](OVERVIEW.md)
4. Contribute improvements

---

## 📊 System Capabilities Matrix

| Capability | Module | Status |
|-----------|--------|--------|
| Video Input | video_capture.py | ✅ Complete |
| Track Detection | track_segmentation.py | ✅ Complete |
| Obstacle Detection | obstacle_detection.py | ✅ Complete |
| False Alert Reduction | multi_frame_confirmation.py | ✅ Complete |
| Distance Estimation | distance_ttc.py | ✅ Complete |
| Severity Classification | severity_classification.py | ✅ Complete |
| Alert System | alert_system.py | ✅ Complete |
| Incident Logging | incident_logging.py | ✅ Complete |
| Analytics | incident_logging.py | ✅ Complete |
| GPU Acceleration | All modules | ✅ Complete |
| Edge Deployment | All modules | ✅ Complete |

---

## 🚀 Quick Start Commands

```bash
# Installation
python setup.py

# Verification  
python verify.py

# Run System
python main.py

# Examples
python examples.py

# Help
python main.py --help
```

---

## 📞 Support & Resources

### Documentation
- **Complete Guide**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Architecture**: [OVERVIEW.md](OVERVIEW.md)
- **Status**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### Configuration
- **Main Config**: [config/config.yaml](config/config.yaml)
- **Edit**: `edit config/config.yaml`

### Scripts
- **Setup**: `python setup.py`
- **Verify**: `python verify.py`
- **Run**: `python main.py`
- **Examples**: `python examples.py`

---

## 🎯 Next Steps

1. ✅ Choose your path:
   - **New User** → [QUICKSTART.md](QUICKSTART.md)
   - **Developer** → [README.md](README.md)
   - **Overview** → [OVERVIEW.md](OVERVIEW.md)

2. ✅ Install system:
   ```bash
   python setup.py
   ```

3. ✅ Run verification:
   ```bash
   python verify.py
   ```

4. ✅ Start using:
   ```bash
   python main.py
   ```

---

## ⚠️ Important Notes

- **Safety**: This is an assistance tool, not a replacement for safety protocols
- **Testing**: Thoroughly test before production deployment
- **Compliance**: Follow all railway safety regulations
- **Configuration**: Review config.yaml before running

---

## 📜 License & Legal

- **License**: MIT License - See [LICENSE](LICENSE)
- **Disclaimer**: See [LICENSE](LICENSE) for safety disclaimer
- **Contributing**: See [README.md](README.md#contributing)

---

**RailTrack AI Safety System v1.0.0**
*Made with ❤️ for Railway Safety*

---

**Navigation**: [Top](#-railtrack---navigation--documentation-index) | [Docs](#-documentation-navigation) | [Files](#-file-organization) | [Quick Start](#-quick-start-commands)
