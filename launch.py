"""
RailTrack - Interactive Launcher
Choose between camera, image, or video file processing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.file_selector import FileSelector, select_image_file, select_video_file, select_media_file
from src.image_processor import ImageProcessor
from main import RailTrackSystem


def show_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("🚆 RAILTRACK AI SAFETY SYSTEM - INTERACTIVE LAUNCHER")
    print("="*70)
    print("\nChoose input source:")
    print("  1. 📹 Live Camera / Webcam")
    print("  2. 🖼️  Single Image File")
    print("  3. 🎥 Video File")
    print("  4. 📁 Choose Media File (Image or Video)")
    print("  5. ❌ Exit")
    print("="*70)


def process_camera():
    """Run with live camera"""
    print("\n🚀 Starting camera mode...")
    system = RailTrackSystem()
    system.run()


def process_image():
    """Process single image"""
    print("\n📂 Select an image file...")
    
    image_path = select_image_file()
    
    if not image_path:
        print("❌ No image selected")
        return
    
    print(f"\n✅ Selected: {image_path}")
    
    # Process image
    processor = ImageProcessor()
    results = processor.process_image(image_path, show_result=True)
    
    if results:
        print(f"\n✅ Image analysis complete!")
        print(f"   Total detections: {len(results['detections'])}")
        print(f"   Total incidents: {len(results['incidents'])}")
        
        # Print incident details
        if results['incidents']:
            print("\n📊 Incident Reports:")
            for i, incident in enumerate(results['incidents'], 1):
                print(f"\n   Incident {i}:")
                print(f"   - Severity: {incident.get('severity', 'unknown').upper()}")
                print(f"   - Type: {incident.get('obstacle', {}).get('type', 'unknown')}")
                print(f"   - Explanation: {incident.get('explanation', 'N/A')[:100]}...")


def process_video():
    """Process video file"""
    print("\n📂 Select a video file...")
    
    video_path = select_video_file()
    
    if not video_path:
        print("❌ No video selected")
        return
    
    print(f"\n✅ Selected: {video_path}")
    print("🚀 Starting video processing...")
    
    # Create system and override video source
    system = RailTrackSystem()
    system.video_capture.camera_config['source'] = video_path
    
    # Restart video capture with new source
    system.video_capture.stop()
    if system.video_capture.start():
        print("✅ Video loaded successfully")
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save screenshot")
        print("  - Press 'r' for report")
        print("  - Press SPACE to pause/resume")
        
        system.run()
    else:
        print("❌ Failed to load video")


def process_media_file():
    """Process media file (auto-detect type)"""
    print("\n📂 Select an image or video file...")
    
    file_path = select_media_file()
    
    if not file_path:
        print("❌ No file selected")
        return
    
    print(f"\n✅ Selected: {file_path}")
    
    # Check file type
    selector = FileSelector()
    
    if selector.is_image(file_path):
        print("📸 Detected: Image file")
        # Process as image
        processor = ImageProcessor()
        results = processor.process_image(file_path, show_result=True)
        
        if results:
            print(f"\n✅ Image analysis complete!")
            print(f"   Total detections: {len(results['detections'])}")
            print(f"   Total incidents: {len(results['incidents'])}")
    
    elif selector.is_video(file_path):
        print("🎥 Detected: Video file")
        # Process as video
        system = RailTrackSystem()
        system.video_capture.camera_config['source'] = file_path
        system.video_capture.stop()
        
        if system.video_capture.start():
            print("✅ Video loaded successfully")
            system.run()
        else:
            print("❌ Failed to load video")
    
    else:
        print("❌ Unsupported file format")


def main():
    """Main launcher function"""
    while True:
        show_menu()
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            process_camera()
        elif choice == '2':
            process_image()
        elif choice == '3':
            process_video()
        elif choice == '4':
            process_media_file()
        elif choice == '5':
            print("\n👋 Exiting RailTrack. Stay safe!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-5.")
        
        # Ask to continue
        if choice in ['1', '2', '3', '4']:
            continue_choice = input("\n🔄 Process another file? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\n👋 Exiting RailTrack. Stay safe!")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        print("👋 Exiting RailTrack. Stay safe!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
