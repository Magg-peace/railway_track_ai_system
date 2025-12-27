# Contributing to RailTrack

Thank you for your interest in contributing to RailTrack! This document provides guidelines for contributing to this project.

## 🌟 Ways to Contribute

- 🐛 **Report Bugs** - Submit detailed bug reports
- 💡 **Suggest Features** - Propose new features or enhancements
- 📖 **Improve Documentation** - Help make our docs better
- 💻 **Submit Code** - Fix bugs or implement features
- 🧪 **Add Tests** - Improve test coverage
- 🎨 **Improve UI/UX** - Enhance visualization or user experience

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/railway_track_ai_system.git
cd railway_track_ai_system
```

### 3. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if any)
pip install pytest black flake8

# Verify installation
python verify.py
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 💻 Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

Example:
```python
def detect_obstacles(frame, model, confidence_threshold=0.5):
    """
    Detect obstacles in a video frame using YOLO model.
    
    Args:
        frame (np.ndarray): Input video frame
        model: YOLOv8 model instance
        confidence_threshold (float): Minimum confidence for detection
        
    Returns:
        list: List of detected obstacles with bounding boxes
    """
    # Implementation here
    pass
```

### Documentation

- Update README.md if adding features
- Add inline comments for complex logic
- Update relevant .md files in docs/ folder
- Include usage examples

### Testing

Before submitting:

```bash
# Run verification
python verify.py

# Test file selection
python test_file_selection.py

# Test with sample data
python examples.py
```

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good ✅
git commit -m "Add support for RTSP camera streams"
git commit -m "Fix false alert issue in multi-frame confirmation"
git commit -m "Update README with deployment instructions"

# Not ideal ❌
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

## 📝 Pull Request Process

### 1. Update Your Fork

```bash
git fetch upstream
git merge upstream/main
```

### 2. Make Your Changes

- Write clean, documented code
- Follow the code style guidelines
- Add tests if applicable
- Update documentation

### 3. Test Your Changes

```bash
# Run all tests
python verify.py
python test_file_selection.py

# Test manually with different scenarios
python launch.py
```

### 4. Commit and Push

```bash
git add .
git commit -m "Descriptive commit message"
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in the PR template:

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Run `python verify.py` to check system

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Open file '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.8.10]
- GPU: [e.g., NVIDIA GTX 1060, CPU only]
- Branch/Commit: [e.g., main/abc1234]

**Logs**
```
Paste relevant logs here
```

**Screenshots**
If applicable
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem Description**
What problem does this solve?

**Proposed Solution**
How would you solve it?

**Alternatives Considered**
What other solutions did you think about?

**Additional Context**
Any other relevant information
```

## 📋 Project Structure

Understanding the codebase:

```
railway_track_ai_system/
├── src/                    # Core modules
│   ├── video_capture.py    # Video input handling
│   ├── obstacle_detection.py  # YOLO detection
│   ├── track_segmentation.py  # Track zone detection
│   └── ...
├── config/                 # Configuration files
├── docs/                   # Documentation
├── utils/                  # Utility functions
├── main.py                # Main application
├── launch.py              # Interactive launcher
└── tests/                 # Test files
```

## 🎯 Areas Needing Help

Current priorities:

1. **Performance Optimization**
   - Improve FPS on edge devices
   - Reduce memory usage
   - Optimize YOLO inference

2. **Additional Features**
   - Web dashboard
   - Database integration
   - Advanced analytics

3. **Documentation**
   - Video tutorials
   - Deployment guides
   - API documentation

4. **Testing**
   - Unit tests
   - Integration tests
   - Edge case handling

## 📞 Getting Help

Need help contributing?

- 💬 Open a discussion on GitHub
- 📧 Contact maintainers
- 📖 Check existing documentation

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in documentation

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making RailTrack better! 🚆🎉**
