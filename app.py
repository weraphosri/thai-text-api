import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

def get_font(size=48):
    """หาฟอนต์ NotoSansThai หรือฟอนต์ไทยที่เหมาะสม"""
    font_paths = [
        # ฟอนต์ที่คุณต้องการ
        '/usr/share/fonts/truetype/noto/NotoSansThai_ExtraCondensed-SemiBold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-SemiBold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        
        # ฟอนต์สำรอง
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
    
    # ใช้ default ถ้าหาไม่เจอ
    return ImageFont.load_default()

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "usage": "POST /text-on-image with JSON body"
    })

@app.route('/test')
def test():
    """ทดสอบรูปง่ายๆ"""
    img = Image.new('RGB', (600, 300), '#4CAF50')
    draw = ImageDraw.Draw(img)
    
    font = get_font(32)
    text = "ทดสอบ NotoSansThai\nHello World 123"
    
    y_pos = 50
    for line in text.split('\n'):
        draw.text((50, y_pos), line, font=font, fill='white')
        y_pos += 50
    
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=85)
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
        
        # โหลดรูป
        response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # หาฟอนต์
        font = get_font(font_size)
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        for i, line in enumerate(lines):
            draw.text((x, y + i * (font_size + 5)), line, font=font, fill=color)
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)