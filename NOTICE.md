# Third-Party Notices & Attributions

This project includes and builds upon several open-source technologies, APIs, and libraries:

## 1. Groq Cloud Whisper API
- **Model**: `whisper-large-v3-turbo`
- **Provider**: [Groq Cloud](https://groq.com/)
- **Description**: Ultra-fast word-level and segment-level timestamp speech recognition.

## 2. FFmpeg & Intel Quick Sync Video (QSV)
- **Tool**: [FFmpeg](https://ffmpeg.org/)
- **Description**: Open-source multimedia framework for audio/video decoding, filtering, and accelerated encoding (`h264_qsv` with `-pix_fmt nv12` / `libx264`).

## 3. Computer Vision & Scientific Python
- **OpenCV (`opencv-python`)**: Image manipulation, compositing, and frame generation.
- **NumPy**: Fast array manipulation, audio RMS envelope extraction, and spectrum computation.
- **Pillow (PIL)**: High-quality anti-aliased font rendering and text overlay generation.

## 4. Fonts
- **Microsoft JhengHei Bold (`msjhbd.ttc`)**: System font on Windows used for zero-tofu CJK lyric rendering.
- **Noto Sans TC**: Open font by Google Fonts (OFL-1.1) recommended for Linux/macOS cross-platform rendering.
