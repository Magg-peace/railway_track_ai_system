# Test Images

Place your test railway track images here for analysis.

## Supported Formats
- JPG/JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## How to Use

1. Copy or download railway track images to this directory
2. Run: `python launch.py`
3. Select option **2** (Process Single Image)
4. Browse and select an image from this folder
5. View detection results

## Sample Images

You can download sample railway track images from:
- Google Images (search: "railway track forward view")
- Kaggle datasets (railway/train datasets)
- YouTube videos (extract frames from railway videos)

## Best Image Characteristics

For optimal detection results:
- **Resolution**: Minimum 640x480, recommended 1920x1080
- **Angle**: Forward-facing view down the tracks
- **Lighting**: Good daylight or use night vision mode
- **Clarity**: Sharp, not blurry or heavily compressed
- **Content**: Railway tracks clearly visible

## Example File Structure

```
test_images/
├── track_clear.jpg
├── track_with_person.jpg
├── track_with_animal.jpg
├── track_with_debris.jpg
├── night_track.jpg
└── curved_track.jpg
```

## Notes

- The system automatically creates `data/processed/` for saving annotated results
- Detection logs are saved in `logs/` directory
- You can process multiple images sequentially using the launch menu
