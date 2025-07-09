import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import tempfile

app = Flask(__name__)

def download_and_cache_font():
    """ดาวน์โหลดและ cache ฟอนต์ไทย"""
    font_path = "/tmp/thai_font.ttf"
    
    if os.path.exists(font_path):
        return font_path
    
    try:
        # ลองดาวน์โหลดจาก CDN หลายแหล่ง
        font_urls = [
            "https://fonts.gstatic.com/s/notosansthai/v20/iJWnBXeUZi_OHPqn4wq6hQ2_hbJ1xyN9wd43SofNWcd1MSTdaD8.ttf",
            "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai-Regular.ttf",
            "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansthai/NotoSansThai-Regular.ttf"
        ]
        
        for url in font_urls:
            try:
                print(f"Trying to download font from: {url}")
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200 and len(response.content) > 10000:  # ฟอนต์ต้องมีขนาดมากกว่า 10KB
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Font downloaded successfully: {len(response.content)} bytes")
                    return font_path
                    
            except Exception as e:
                print(f"Failed to download from {url}: {e}")
                continue
        
        print("All font download attempts failed")
        return None
        
    except Exception as e:
        print(f"Font download error: {e}")
        return None

def get_best_font(size=48):
    """หาฟอนต์ที่ดีที่สุด"""
    # ลองใช้ฟอนต์ที่ดาวน์โหลด
    downloaded_font = download_and_cache_font()
    if downloaded_font:
        try:
            font = ImageFont.truetype(downloaded_font, size)
            print(f"Using downloaded Thai font: {downloaded_font}")
            return font, True  # True = มีฟอนต์ไทย
        except Exception as e:
            print(f"Failed to load downloaded font: {e}")
    
    # ลองหาฟอนต์ในระบบ
    system_fonts = [
        '/System/Library/Fonts/Helvetica.ttc',  # macOS
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        'C:/Windows/Fonts/arial.ttf',  # Windows
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size)
                print(f"Using system font: {font_path}")
                return font, False  # False = ไม่ใช่ฟอนต์ไทย
            except:
                continue
    
    # ใช้ default font
    print("Using default font")
    return ImageFont.load_default(), False

@app.route('/')
def home():
    font, is_thai = get_best_font(20)
    font_status = "✅ Thai font loaded" if is_thai else "⚠️ Using fallback font"
    
    return jsonify({
        "status": "Thai Text API ✅",
        "font_support": font_status,
        "info": "Simple and reliable Thai text API",
        "endpoints": {
            "/text-on-image": "POST - เพิ่มข้อความบนรูป",
            "/test": "GET - ทดสอบ",
            "/simple-test": "GET - ทดสอบง่ายๆ"
        }
    })

@app.route('/simple-test')
def simple_test():
    """ทดสอบแบบง่ายๆ"""
    # สร้างรูปพื้นฐาน
    img = Image.new('RGB', (600, 300), '#4CAF50')
    draw = ImageDraw.Draw(img)
    
    # ทดสอบข้อความ
    test_texts = [
        "Hello World (English)",
        "สวัสดีครับ (Thai)",
        "ทดสอบ ABC 123"
    ]
    
    font, is_thai = get_best_font(32)
    
    y_pos = 50
    for text in test_texts:
        draw.text((50, y_pos), text, font=font, fill='white')
        y_pos += 50
    
    # แสดงสถานะฟอนต์
    status_font, _ = get_best_font(16)
    status = "✅ Thai Font Loaded" if is_thai else "⚠️ Fallback Font (may show squares)"
    draw.text((50, 220), status, font=status_font, fill='yellow')
    
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/test')
def test():
    """ทดสอบแบบละเอียด"""
    img = Image.new('RGB', (800, 500), '#2196F3')
    draw = ImageDraw.Draw(img)
    
    font, is_thai = get_best_font(36)
    small_font, _ = get_best_font(20)
    
    # ข้อความทดสอบ
    if is_thai:
        test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
        status = "✅ Perfect! Thai font working"
        color = '#4CAF50'
    else:
        test_text = "Thai text may show as squares\nทดสอบ ภาษาไทย\nHello World"
        status = "⚠️ No Thai font - using fallback"
        color = '#FF9800'
    
    # วาดข้อความ
    lines = test_text.split('\n')
    y_pos = 80
    for line in lines:
        draw.text((50, y_pos), line, font=font, fill='white')
        y_pos += 60
    
    # สถานะ
    draw.text((50, 350), status, font=small_font, fill=color)
    draw.text((50, 380), f"Font loaded: {'Yes' if is_thai else 'Fallback'}", 
             font=small_font, fill='white')
    
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/text-on-image', methods=['POST'])
def add_text():
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 50))
        y = int(data.get('y', 50))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # โหลดรูปภาพ
        print(f"Downloading image from: {img_url}")
        img_response = requests.get(img_url, timeout=15)
        img_response.raise_for_status()
        
        img = Image.open(BytesIO(img_response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # หาฟอนต์
        font, is_thai = get_best_font(font_size)
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_y = y + (i * (font_size + 10))
            draw.text((x, text_y), line, font=font, fill=color)
        
        # เพิ่มคำเตือนถ้าไม่มีฟอนต์ไทย
        if not is_thai and any('\u0E00' <= char <= '\u0E7F' for char in text):
            warning_font, _ = get_best_font(16)
            draw.text((10, 10), "⚠️ Thai font not available", 
                     font=warning_font, fill='red')
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=95, optimize=True)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Cannot load image: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)