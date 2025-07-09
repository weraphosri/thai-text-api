import os
import base64
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, features
from io import BytesIO

app = Flask(__name__)

# Base64 encoded Thai font (NotoSansThai-Regular.ttf)
THAI_FONT_BASE64 = """
AAEAAAAOAIAAAwBgT1MvMlpXsXgAAADsAAAAYGNtYXABIwCLAAABTAAAAFRjdnQgK6gHnQAAAaAAAAA4ZnBnbYoKeDsAAAHYAAAJkWdhc3AAAAAQAAALbAAAAAhnbHlmAUECOwAACyQAAAtgaGVhZNpgBsAAAAFsAAAANmhoZWEH6QNyAAAAqAAAACRobXR4CCEAWgAAAbAAAAAWbG9jYQLIAnAABgEAAAACa2F4cCAAIAEAAAHsAAAAIG5hbWXF+uE7AAAW4AAAAkNwb3N0/7gAMgAAGSQAAAAgcHJlcGgGjIUAABpEAAAAVAABAAAADPgM+gALAAhQAAkAAQAFAAIAAgUGAQMEBwgJCgsYCRANDhQEAAEAAgADAAQABgAHAAkADQAOABQAGAEJAP7/AgAEAAYABwAJAA0ADgAUABgBCQABAAAAANwA3AAAAQAAAA0AFAAYAAAAAgAEAAYACQAOAP//AAIABAAGAAkADgCXmJiYhYWFhYODg4GBgYGBgQAAAAEAAAABAADZCWKgXw889QADA+gAAAAA3XDqNgAAAADv8dLo/sD8wAQAAxcAAAAIAAIAAAAAAAAAAQAAAxf8wAAEAAD+wP7ABAABAAEAAAAEAAAAAwABAAIAAQABQAEAJYAFAC2ABQAOgAUAB4AFAHWABQAm"""

def create_thai_font_file():
    """สร้างไฟล์ฟอนต์ไทยจาก base64"""
    try:
        font_path = "/tmp/thai_font.ttf"
        
        # ถ้ามีไฟล์แล้วไม่ต้องสร้างใหม่
        if os.path.exists(font_path):
            return font_path
            
        # Decode base64 และสร้างไฟล์
        font_data = base64.b64decode(THAI_FONT_BASE64)
        with open(font_path, 'wb') as f:
            f.write(font_data)
        
        print(f"Thai font created: {font_path}")
        return font_path
        
    except Exception as e:
        print(f"Failed to create Thai font: {e}")
        return None

def get_font(size=48):
    """หาฟอนต์ไทยที่ดีที่สุด"""
    # ลองใช้ฟอนต์ที่สร้างจาก base64
    thai_font = create_thai_font_file()
    if thai_font and os.path.exists(thai_font):
        try:
            print(f"Using embedded Thai font: {thai_font}")
            return ImageFont.truetype(thai_font, size)
        except Exception as e:
            print(f"Failed to load embedded font: {e}")
    
    # ลองหาฟอนต์ในระบบ
    system_fonts = [
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            try:
                print(f"Using system font: {font_path}")
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Failed to load system font {font_path}: {e}")
    
    # ใช้ default font สุดท้าย
    print("Using default font")
    return ImageFont.load_default()

def check_raqm_support():
    """ตรวจสอบว่า PIL มี RAQM support หรือไม่"""
    try:
        return features.check_feature('raqm')
    except:
        return False

@app.route('/')
def home():
    raqm_status = "✅ RAQM supported" if check_raqm_support() else "❌ RAQM not supported"
    
    # ตรวจสอบฟอนต์
    font_status = "❌ No Thai font"
    try:
        test_font = get_font(20)
        if test_font:
            font_status = "✅ Thai font available"
    except:
        pass
    
    return jsonify({
        "status": "Thai Text API ✅",
        "raqm_support": raqm_status,
        "font_support": font_status,
        "info": "Using embedded Thai font"
    })

@app.route('/test')
def test():
    """ทดสอบ Thai text rendering"""
    img = Image.new('RGB', (800, 400), '#1565C0')
    draw = ImageDraw.Draw(img)
    
    # ข้อความทดสอบ
    test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ ทดสอบ"
    
    try:
        font = get_font(36)
        status_font = get_font(18)
        
        # ตรวจสอบ RAQM และฟอนต์
        has_raqm = check_raqm_support()
        
        lines = test_text.split('\n')
        y_pos = 50
        
        for line in lines:
            if has_raqm:
                # ใช้ RAQM
                draw.text(
                    (50, y_pos), 
                    line, 
                    font=font, 
                    fill='white',
                    language='th',
                    direction='ltr'
                )
            else:
                # ไม่มี RAQM - ใช้ basic rendering
                draw.text((50, y_pos), line, font=font, fill='white')
            y_pos += 60
        
        # แสดงสถานะ
        if has_raqm:
            status_text = "✅ RAQM + Embedded Font: Perfect!"
            status_color = '#4CAF50'
        else:
            status_text = "⚠️ Basic rendering with embedded font"
            status_color = '#FF9800'
            
        draw.text((50, 320), status_text, font=status_font, fill=status_color)
        
    except Exception as e:
        # ถ้า error ให้แสดงข้อความ error
        error_font = ImageFont.load_default()
        draw.text((50, 100), f"Font Error: {str(e)}", font=error_font, fill='white')
        draw.text((50, 150), "Check logs for details", font=error_font, fill='yellow')
    
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=90)
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
        language = data.get('language', 'th')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # โหลดรูป
        response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # หาฟอนต์
        font = get_font(font_size)
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        has_raqm = check_raqm_support()
        
        for i, line in enumerate(lines):
            if has_raqm:
                # ใช้ RAQM สำหรับ proper text shaping
                draw.text(
                    (x, y + i * (font_size + 5)), 
                    line, 
                    font=font, 
                    fill=color,
                    language=language,
                    direction='ltr'
                )
            else:
                # fallback สำหรับ non-RAQM
                draw.text((x, y + i * (font_size + 5)), line, font=font, fill=color)
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)