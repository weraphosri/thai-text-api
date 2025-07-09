import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, features
from io import BytesIO

app = Flask(__name__)

def get_thai_font(size=48):
    """หาฟอนต์ไทยจาก Noto fonts"""
    font_paths = [
        # Noto fonts ใน Nixpacks
        '/nix/store/*/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/nix/store/*/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        
        # System fonts fallback
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    # ใช้ glob เพื่อหา Nix store paths
    import glob
    for pattern in font_paths:
        if '*' in pattern:
            matches = glob.glob(pattern)
            if matches:
                font_paths.extend(matches)
        elif os.path.exists(pattern):
            try:
                return ImageFont.truetype(pattern, size)
            except:
                continue
    
    # ใช้ default font
    return ImageFont.load_default()

def has_raqm():
    """ตรวจสอบว่ามี RAQM support"""
    try:
        return features.check_feature('raqm')
    except:
        return False

@app.route('/')
def home():
    raqm_status = "✅ RAQM available" if has_raqm() else "❌ RAQM not available"
    
    return jsonify({
        "status": "Thai Text API with Nixpacks ✅",
        "raqm_support": raqm_status,
        "info": "Uses Noto fonts with RAQM for proper Thai rendering"
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    img = Image.new('RGB', (800, 400), '#673AB7')
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
        draw.text((50, 320), "✅ RAQM + Noto Thai Font: Perfect rendering!", 
                 font=small_font, fill='#4CAF50')
    else:
        # Fallback แบบง่าย
        lines = test_text.split('\n')
        y_pos = 50
        for line in lines:
            draw.text((50, y_pos), line, font=font, fill='white')
            y_pos += 60
        
        draw.text((50, 320), "⚠️ No RAQM: Basic rendering only", 
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