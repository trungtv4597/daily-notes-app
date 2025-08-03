# Images Directory

This directory contains images and assets for the Daily Notes Streamlit application.

## Recommended Images

- `logo.png` - Application logo (recommended size: 200x200px)
- `header.png` - Header banner image (recommended size: 1200x300px)
- `favicon.ico` - Browser favicon (16x16px or 32x32px)

## Usage

Images can be loaded in Streamlit using:

```python
import streamlit as st
from PIL import Image

# Load and display logo
logo = Image.open('assets/images/logo.png')
st.image(logo, width=200)

# Load and display header
header = Image.open('assets/images/header.png')
st.image(header, use_column_width=True)
```

## File Formats

Supported formats:
- PNG (recommended for logos and graphics)
- JPG/JPEG (recommended for photos)
- SVG (for vector graphics)
- GIF (for animations)
