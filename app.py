import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, features
import requests
from io import BytesIO

app = Flask(__name__)

def check_raqm_support():
    """ตรวจสอบว่า PIL มี RAQM support หรือไม่"""
    return features.check_feature('raqm')

def get_font(size=48):
    """หาฟอนต์ที่รองรับภาษาไทย"""
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansThai_ExtraCondensed-SemiBold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-SemiBold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    
    return ImageFont.load_default()

@app.route('/')
def home():
    raqm_status = "✅ RAQM supported" if check_raqm_support() else "❌ RAQM not supported"
    return jsonify({
        "status": "Thai Text API ✅",
        "raqm_support": raqm_status,
        "info": "RAQM required for proper Thai text rendering"
    })

@app.route('/test')
def test():
    """ทดสอบ Thai text shaping"""
    img = Image.new('RGB', (800, 400), '#2E7D32')
    draw = ImageDraw.Draw(img)
    
    # ข้อความทดสอบที่มีปัญหาสระลอย
    test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
    font = get_font(36)
    
    # ตรวจสอบ RAQM support
    if check_raqm_support():
        # ใช้ RAQM สำหรับ complex text shaping
        lines = test_text.split('\n')
        y_pos = 50
        for line in lines:
            draw.text(
                (50, y_pos), 
                line, 
                font=font, 
                fill='white',
                language='th',  # บอก language เป็นภาษาไทย
                direction='ltr'  # left-to-right
            )
            y_pos += 60
        
        # เพิ่มข้อความแสดงสถานะ
        status_font = get_font(20)
        draw.text((50, 320), "✅ RAQM: Thai text shaped correctly", 
                 font=status_font, fill='#FFEB3B')
    else:
        # ถ้าไม่มี RAQM ให้แสดงคำเตือน
        lines = test_text.split('\n')
        y_pos = 50
        for line in lines:
            draw.text((50, y_pos), line, font=font, fill='white')
            y_pos += 60
        
        status_font = get_font(20)
        draw.text((50, 320), "❌ No RAQM: May have sara loy issues", 
                 font=status_font, fill='#F44336')
    
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
        language = data.get('language', 'th')  # Default เป็นภาษาไทย
        
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
        
        if check_raqm_support():
            # ใช้ RAQM สำหรับ proper Thai text shaping
            for i, line in enumerate(lines):
                draw.text(
                    (x, y + i * (font_size + 5)), 
                    line, 
                    font=font, 
                    fill=color,
                    language=language,  # ใช้ภาษาที่ผู้ใช้ระบุ
                    direction='ltr'
                )
        else:
            # fallback สำหรับ non-RAQM
            for i, line in enumerate(lines):
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