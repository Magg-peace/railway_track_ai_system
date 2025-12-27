"""
RailTrack - Setup and Installation Script
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_directories():
    """Create necessary directories"""
    print("\nCreating directory structure...")
    
    directories = [
        "models",
        "data",
        "logs",
        "logs/images",
        "logs/incidents",
        "config",
        "src",
        "utils",
        "alerts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True, parents=True)
        print(f"✅ Created: {directory}/")
    
    print("✅ Directory structure created")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def download_yolo_model():
    """Download YOLOv8 model"""
    print("\nDownloading YOLOv8 model...")
    
    try:
        # Import will trigger download if model doesn't exist
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        
        # Move to models directory
        if not Path('models/yolov8n.pt').exists():
            import shutil
            shutil.move('yolov8n.pt', 'models/yolov8n.pt')
        
        print("✅ YOLOv8 model downloaded")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not download model: {e}")
        print("Model will be downloaded on first run")
        return True


def check_cuda():
    """Check CUDA availability"""
    print("\nChecking CUDA availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            return True
        else:
            print("⚠️ CUDA not available, will use CPU")
            return True
            
    except ImportError:
        print("⚠️ PyTorch not installed yet")
        return True


def create_sample_env():
    """Create sample .env file"""
    print("\nCreating sample environment file...")
    
    env_content = """# RailTrack Environment Variables

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=railtrack

# OpenAI Configuration (for Explainable AI)
OPENAI_API_KEY=your_openai_api_key

# System Configuration
TRAIN_SPEED_KMH=60
GPS_ENABLED=false
DEBUG_MODE=true
"""
    
    env_file = Path(".env.example")
    
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env.example file")
    else:
        print("⚠️ .env.example already exists")
    
    return True


def verify_installation():
    """Verify installation by importing modules"""
    print("\nVerifying installation...")
    
    required_modules = [
        'cv2',
        'numpy',
        'yaml',
        'ultralytics',
        'torch'
    ]
    
    failed = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required modules available")
    return True


def main():
    """Main setup function"""
    print("="*60)
    print("🚆 RAILTRACK SETUP")
    print("="*60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
        ("Downloading YOLOv8 model", download_yolo_model),
        ("Checking CUDA", check_cuda),
        ("Creating environment file", create_sample_env),
        ("Verifying installation", verify_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"Step: {step_name}")
        print('='*60)
        
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit config/config.yaml with your settings")
    print("2. Configure alerts in config/config.yaml")
    print("3. Run: python main.py")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
