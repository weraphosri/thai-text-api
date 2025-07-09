FROM python:3.11-slim

# ติดตั้ง dependencies สำหรับ RAQM และ Thai fonts
RUN apt-get update && apt-get install -y \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    fonts-noto-cjk \
    fonts-thai-tlwg \
    meson \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Pillow with RAQM support
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]