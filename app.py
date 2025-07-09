import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, features
from io import BytesIO

app = Flask(__name__)

def get_thai_font(size=48):
    """หาฟอนต์ไทยที่ดีที่สุด"""
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Failed to load {font_path}: {e}")
                continue
    
    # Default font
    return ImageFont.load_default()

def has_raqm():
    """ตรวจสอบ RAQM support"""
    try:
        return features.check_feature('raqm')
    except:
        return False

@app.route('/')
def home():
    raqm_status = "✅ RAQM available" if has_raqm() else "❌ RAQM not available"
    
    # ตรวจสอบฟอนต์ไทย
    font_files = [
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf'
    ]
    
    font_status = []
    for font_file in font_files:
        if os.path.exists(font_file):
            font_status.append(f"✅ {os.path.basename(font_file)}")
        else:
            font_status.append(f"❌ {os.path.basename(font_file)}")
    
    return jsonify({
        "status": "Thai Text API Final Version ✅",
        "raqm_support": raqm_status,
        "fonts": font_status,
        "info": "With Dockerfile for guaranteed Thai support"
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    img = Image.new('RGB', (800, 400), '#1976D2')
    draw = ImageDraw.Draw(img)
    
    # ข้อความทดสอบ
    test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
    
    font = get_thai_font(36)
    small_font = get_thai_font(20)
    
    # ใช้ RAQM ถ้ามี
    if has_raqm():
        lines = test_text.split('\n')
        y_pos = 50
        for line in lines:
            draw.text(
                (50, y_pos), 
                line, 
                font=font, 
                fill='white',
                language='th',
                direction='ltr'
            )
            y_pos += 60
        
        # แสดงสถานะ
        draw.text((50, 320), "✅ RAQM + Noto Thai: Perfect Thai rendering!", 
                 font=small_font, fill='#4CAF50')
    else:
        # Fallback แบบง่าย
        lines = test_text.split('\n')
        y_pos = 50
        for line in lines:
            draw.text((50, y_pos), line, font=font, fill='white')
            y_pos += 60
        
        draw.text((50, 320), "⚠️ No RAQM: May have rendering issues", 
                 font=small_font, fill='#FF9800')
    
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
        img_response = requests.get(img_url, timeout=15)
        img_response.raise_for_status()
        
        img = Image.open(BytesIO(img_response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        font = get_thai_font(font_size)
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            text_y = y + (i * (font_size + 10))
            
            if has_raqm():
                # ใช้ RAQM สำหรับ proper Thai rendering
                draw.text(
                    (x, text_y), 
                    line, 
                    font=font, 
                    fill=color,
                    language='th',
                    direction='ltr'
                )
            else:
                # Fallback
                draw.text((x, text_y), line, font=font, fill=color)
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)