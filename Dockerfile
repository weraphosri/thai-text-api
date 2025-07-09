FROM python:3.11-slim

# ติดตั้ง dependencies สำหรับ RAQM
RUN apt-get update && apt-get install -y \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    fonts-thai-tlwg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements และติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy ฟอนต์และโค้ด
COPY fonts/ fonts/
COPY . .

CMD ["python", "app.py"]