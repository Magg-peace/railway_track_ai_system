"""
RailTrack - File Selector
Interactive file selection for images and videos
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Optional, List


class FileSelector:
    """GUI file selector for images and videos"""
    
    def __init__(self):
        """Initialize file selector"""
        self.root = None
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    
    def select_file(self, file_type: str = "both") -> Optional[str]:
        """
        Open file dialog to select image or video
        
        Args:
            file_type: "image", "video", or "both"
            
        Returns:
            Selected file path or None
        """
        # Create root window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.attributes('-topmost', True)
        
        # Prepare file type filters
        if file_type == "image":
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All files", "*.*")
            ]
            title = "Select an Image"
        elif file_type == "video":
            filetypes = [
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
            title = "Select a Video"
        else:  # both
            filetypes = [
                ("Media files", "*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov *.mkv"),
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
            title = "Select an Image or Video"
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        
        # Cleanup
        self.root.destroy()
        
        return file_path if file_path else None
    
    def select_multiple_files(self, file_type: str = "both") -> List[str]:
        """
        Open file dialog to select multiple images or videos
        
        Args:
            file_type: "image", "video", or "both"
            
        Returns:
            List of selected file paths
        """
        # Create root window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.attributes('-topmost', True)
        
        # Prepare file type filters
        if file_type == "image":
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All files", "*.*")
            ]
            title = "Select Images"
        elif file_type == "video":
            filetypes = [
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
            title = "Select Videos"
        else:  # both
            filetypes = [
                ("Media files", "*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov *.mkv"),
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
            title = "Select Images or Videos"
        
        # Open file dialog
        file_paths = filedialog.askopenfilenames(
            title=title,
            filetypes=filetypes
        )
        
        # Cleanup
        self.root.destroy()
        
        return list(file_paths) if file_paths else []
    
    def is_image(self, file_path: str) -> bool:
        """Check if file is an image"""
        return Path(file_path).suffix.lower() in self.supported_image_formats
    
    def is_video(self, file_path: str) -> bool:
        """Check if file is a video"""
        return Path(file_path).suffix.lower() in self.supported_video_formats


def select_media_file() -> Optional[str]:
    """
    Quick function to select an image or video file
    
    Returns:
        Selected file path or None
    """
    selector = FileSelector()
    return selector.select_file("both")


def select_image_file() -> Optional[str]:
    """
    Quick function to select an image file
    
    Returns:
        Selected file path or None
    """
    selector = FileSelector()
    return selector.select_file("image")


def select_video_file() -> Optional[str]:
    """
    Quick function to select a video file
    
    Returns:
        Selected file path or None
    """
    selector = FileSelector()
    return selector.select_file("video")


if __name__ == "__main__":
    # Test file selector
    print("Testing File Selector...")
    
    selector = FileSelector()
    
    print("\nSelect a media file (image or video):")
    file_path = selector.select_file("both")
    
    if file_path:
        print(f"✅ Selected: {file_path}")
        
        if selector.is_image(file_path):
            print("   Type: Image")
        elif selector.is_video(file_path):
            print("   Type: Video")
    else:
        print("❌ No file selected")
