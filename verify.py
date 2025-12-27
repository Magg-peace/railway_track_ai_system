"""
RailTrack - System Verification Script
Verifies that all components are correctly installed and configured
"""

import sys
from pathlib import Path
import importlib


def check_file_structure():
    """Verify project file structure"""
    print("Checking file structure...")
    
    required_files = [
        'main.py',
        'setup.py',
        'requirements.txt',
        'README.md',
        'config/config.yaml',
        'src/video_capture.py',
        'src/track_segmentation.py',
        'src/obstacle_detection.py',
        'src/multi_frame_confirmation.py',
        'src/distance_ttc.py',
        'src/severity_classification.py',
        'src/alert_system.py',
        'src/incident_logging.py',
        'utils/helpers.py'
    ]
    
    required_dirs = [
        'src',
        'config',
        'models',
        'data',
        'logs',
        'utils',
        'alerts'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ {file}")
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
            print(f"  ❌ Missing directory: {directory}/")
        else:
            print(f"  ✅ {directory}/")
    
    if missing_files or missing_dirs:
        print(f"\n❌ Missing {len(missing_files)} files and {len(missing_dirs)} directories")
        return False
    
    print("\n✅ All files and directories present")
    return True


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'yaml': 'pyyaml',
        'ultralytics': 'ultralytics',
        'torch': 'torch',
        'PIL': 'Pillow'
    }
    
    missing = []
    
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_modules():
    """Check if custom modules can be imported"""
    print("\nChecking custom modules...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules = [
        'src.video_capture',
        'src.track_segmentation',
        'src.obstacle_detection',
        'src.multi_frame_confirmation',
        'src.distance_ttc',
        'src.severity_classification',
        'src.alert_system',
        'src.incident_logging',
        'utils.helpers'
    ]
    
    failed = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {str(e)[:50]}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import {len(failed)} modules")
        return False
    
    print("\n✅ All modules imported successfully")
    return True


def check_configuration():
    """Check configuration file"""
    print("\nChecking configuration...")
    
    try:
        import yaml
        
        config_file = Path('config/config.yaml')
        
        if not config_file.exists():
            print("  ❌ config.yaml not found")
            return False
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        required_sections = [
            'system',
            'camera',
            'video',
            'yolo',
            'track',
            'confirmation',
            'distance',
            'severity',
            'alerts',
            'logging'
        ]
        
        missing = []
        for section in required_sections:
            if section in config:
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section} section missing")
                missing.append(section)
        
        if missing:
            print(f"\n❌ Missing configuration sections: {', '.join(missing)}")
            return False
        
        print("\n✅ Configuration file valid")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading config: {e}")
        return False


def check_gpu():
    """Check GPU availability"""
    print("\nChecking GPU...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"  ✅ CUDA available")
            print(f"  ✅ Device: {torch.cuda.get_device_name(0)}")
            print(f"  ✅ CUDA version: {torch.version.cuda}")
            return True
        else:
            print("  ⚠️ CUDA not available (will use CPU)")
            return True
            
    except ImportError:
        print("  ⚠️ PyTorch not installed (cannot check GPU)")
        return True
    except Exception as e:
        print(f"  ⚠️ Error checking GPU: {e}")
        return True


def check_yolo_model():
    """Check if YOLO model exists"""
    print("\nChecking YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        model_paths = [
            'models/yolov8n.pt',
            'yolov8n.pt'
        ]
        
        model_found = False
        for path in model_paths:
            if Path(path).exists():
                print(f"  ✅ Model found at {path}")
                model_found = True
                break
        
        if not model_found:
            print("  ⚠️ YOLOv8 model not found")
            print("  ℹ️ Model will be downloaded on first run")
        
        return True
        
    except ImportError:
        print("  ❌ Ultralytics YOLO not installed")
        return False
    except Exception as e:
        print(f"  ⚠️ Error checking model: {e}")
        return True


def run_quick_test():
    """Run a quick functionality test"""
    print("\nRunning quick functionality test...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test video capture
        from src.video_capture import VideoCapture
        capture = VideoCapture()
        print("  ✅ VideoCapture initialized")
        
        # Test track segmentation
        from src.track_segmentation import TrackSegmentation
        tracker = TrackSegmentation()
        print("  ✅ TrackSegmentation initialized")
        
        # Test obstacle detector
        from src.obstacle_detection import ObstacleDetector
        detector = ObstacleDetector()
        print("  ✅ ObstacleDetector initialized")
        
        # Test severity classifier
        from src.severity_classification import SeverityClassifier
        classifier = SeverityClassifier()
        print("  ✅ SeverityClassifier initialized")
        
        # Test alert manager
        from src.alert_system import AlertManager
        alert_mgr = AlertManager()
        print("  ✅ AlertManager initialized")
        
        print("\n✅ All core components functional")
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False


def main():
    """Main verification function"""
    print("="*70)
    print("🚆 RAILTRACK SYSTEM VERIFICATION")
    print("="*70)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Custom Modules", check_modules),
        ("Configuration", check_configuration),
        ("GPU Support", check_gpu),
        ("YOLO Model", check_yolo_model),
        ("Functionality", run_quick_test)
    ]
    
    results = {}
    
    for name, check_func in checks:
        print(f"\n{'='*70}")
        print(f"Check: {name}")
        print('='*70)
        results[name] = check_func()
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("="*70)
        print("\nSystem is ready to use!")
        print("\nNext steps:")
        print("  1. Review config/config.yaml")
        print("  2. Run: python main.py")
        print("  3. Check examples: python examples.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*70)
        print("\nPlease fix the issues above before running the system")
        print("Run: python setup.py to install missing components")
    
    print("\n" + "="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
