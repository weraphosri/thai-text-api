FROM python:3.11-slim

# ติดตั้ง system dependencies สำหรับ RAQM และ Thai fonts
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libraqm-dev \
    pkg-config \
    build-essential \
    curl \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# ดาวน์โหลดและติดตั้ง Noto Thai fonts
RUN mkdir -p /usr/share/fonts/truetype/noto && \
    curl -L "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai-Regular.ttf" \
    -o /usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf && \
    curl -L "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai-Bold.ttf" \
    -o /usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf && \
    fc-cache -fv

WORKDIR /app

# ติดตั้ง Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# ตรวจสอบว่า RAQM ติดตั้งสำเร็จ
RUN python -c "from PIL import features; print('RAQM:', features.check_feature('raqm'))"

CMD ["python", "app.py"]