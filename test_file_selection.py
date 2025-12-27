#!/usr/bin/env python3
"""
Test script for file selection functionality
Tests the FileSelector class without requiring actual GUI interaction
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from file_selector import FileSelector


def test_file_type_detection():
    """Test image and video file type detection"""
    print("Testing file type detection...")
    
    selector = FileSelector()
    
    # Test image files
    image_files = [
        "test.jpg", "test.jpeg", "test.png", 
        "test.bmp", "test.tiff", "TEST.JPG"
    ]
    
    for file in image_files:
        assert selector.is_image(file), f"Failed to detect {file} as image"
        print(f"✓ {file} correctly detected as image")
    
    # Test video files
    video_files = [
        "test.mp4", "test.avi", "test.mov", 
        "test.mkv", "test.flv", "test.wmv", "TEST.MP4"
    ]
    
    for file in video_files:
        assert selector.is_video(file), f"Failed to detect {file} as video"
        print(f"✓ {file} correctly detected as video")
    
    # Test non-media files
    other_files = ["test.txt", "test.pdf", "test.doc"]
    
    for file in other_files:
        assert not selector.is_image(file), f"Incorrectly detected {file} as image"
        assert not selector.is_video(file), f"Incorrectly detected {file} as video"
        print(f"✓ {file} correctly detected as non-media")
    
    print("\n✅ All file type detection tests passed!")


def test_path_object_handling():
    """Test that FileSelector can handle Path objects"""
    print("\nTesting Path object handling...")
    
    selector = FileSelector()
    
    # Test with Path objects
    image_path = Path("test.jpg")
    video_path = Path("test.mp4")
    
    assert selector.is_image(image_path), "Failed with Path object for image"
    assert selector.is_video(video_path), "Failed with Path object for video"
    
    print("✓ Path objects handled correctly")
    print("\n✅ Path object tests passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("RailTrack File Selection Tests")
    print("=" * 60)
    print()
    
    try:
        test_file_type_detection()
        test_path_object_handling()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nFile selection module is working correctly.")
        print("You can now run: python launch.py")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
