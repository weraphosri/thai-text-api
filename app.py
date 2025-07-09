import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
from io import BytesIO
import sys
import unicodedata

# ตั้งค่า encoding เป็น UTF-8
if sys.version_info[0] >= 3:
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

def fix_thai_text(text):
    """แก้ปัญหาสระลอยสำหรับภาษาไทย"""
    if not text:
        return text
    
    # Normalize Unicode
    text = unicodedata.normalize('NFC', text)
    
    # รายการสระบนและสระล่าง
    thai_vowels_above = ['ิ', 'ี', 'ึ', 'ื', '่', '้', '๊', '๋', '็', '์']
    thai_vowels_below = ['ุ', 'ู']
    
    fixed_text = ""
    for i, char in enumerate(text):
        if char in thai_vowels_above or char in thai_vowels_below:
            # ตรวจสอบว่าตัวก่อนหน้าเป็นตัวอักษรไทยหรือไม่
            if i > 0 and '\u0E00' <= text[i-1] <= '\u0E7F':
                # เพิ่ม Zero Width Space เพื่อช่วยในการ rendering
                fixed_text += '\u200B' + char
            else:
                fixed_text += char
        else:
            fixed_text += char
    
    return fixed_text

def get_thai_font(size=48):
    """หาฟอนต์ภาษาไทยที่ดีที่สุด"""
    thai_fonts = [
        # ฟอนต์ Linux
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Loma-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Loma.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        
        # ฟอนต์ Windows (สำหรับ local testing)
        'C:/Windows/Fonts/tahoma.ttf',
        'C:/Windows/Fonts/tahomabd.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        
        # ฟอนต์ macOS
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
    ]
    
    for font_path in thai_fonts:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"ไม่สามารถโหลดฟอนต์ {font_path}: {e}")
            continue
    
    # ถ้าหาฟอนต์ไม่เจอ ใช้ default
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def add_text_with_stroke(draw, text, position, font, fill_color, stroke_color, stroke_width):
    """เพิ่มข้อความพร้อม stroke effect"""
    x, y = position
    
    # วาด stroke หลายรอบเพื่อให้หนา
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    # วาดข้อความหลัก
    draw.text(position, text, font=font, fill=fill_color)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API is running! ✅",
        "endpoints": {
            "/text-on-image": "POST - เพิ่มข้อความบนรูปภาพ",
            "/test": "GET - ทดสอบการทำงาน",
            "/fonts": "GET - ดูฟอนต์ที่มี"
        },
        "example": {
            "url": "/text-on-image",
            "method": "POST",
            "body": {
                "img_url": "https://picsum.photos/800/600",
                "text": "สวัสดีครับ ทดสอบภาษาไทย",
                "x": 100,
                "y": 100,
                "font_size": 48,
                "font_color": "#FFFFFF",
                "stroke_width": 3,
                "stroke_color": "#000000"
            }
        }
    })

@app.route('/fonts')
def list_fonts():
    """แสดงรายการฟอนต์ที่ใช้ได้"""
    available_fonts = []
    thai_fonts = [
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Loma-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    
    for font_path in thai_fonts:
        if os.path.exists(font_path):
            available_fonts.append({
                "path": font_path,
                "name": os.path.basename(font_path),
                "status": "available"
            })
    
    return jsonify({
        "available_fonts": available_fonts,
        "total": len(available_fonts)
    })

@app.route('/test')
def test():
    """ทดสอบการสร้างรูปภาพ"""
    try:
        # สร้างรูปทดสอบ
        img = Image.new('RGB', (800, 400), color='#2196F3')
        draw = ImageDraw.Draw(img)
        
        # ข้อความทดสอบ
        test_text = "ทดสอบภาษาไทย\nสวัสดีครับ ยินดีต้อนรับ\nที่นี่ ยิ้ม สิ้นสุด"
        fixed_text = fix_thai_text(test_text)
        
        # หาฟอนต์
        font = get_thai_font(36)
        
        # เพิ่มข้อความ
        lines = fixed_text.split('\n')
        y_offset = 50
        for line in lines:
            add_text_with_stroke(
                draw=draw,
                text=line,
                position=(50, y_offset),
                font=font,
                fill_color='#FFFFFF',
                stroke_color='#000000',
                stroke_width=2
            )
            y_offset += 60
        
        # บันทึกและส่งกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text-on-image', methods=['POST'])
def text_on_image():
    try:
        data = request.get_json()
        
        # พารามิเตอร์
        img_url = data.get('img_url')
        text = data.get('text', 'Hello World')
        x = int(data.get('x', 50))
        y = int(data.get('y', 50))
        font_size = int(data.get('font_size', 48))
        font_color = data.get('font_color', '#FFFFFF')
        stroke_width = int(data.get('stroke_width', 2))
        stroke_color = data.get('stroke_color', '#000000')
        
        # ตรวจสอบ URL
        if not img_url:
            return jsonify({"error": "กรุณาระบุ img_url"}), 400
        
        # ดาวน์โหลดรูปภาพ
        try:
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            
            # แปลงเป็น RGB ถ้าไม่ใช่
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
        except Exception as e:
            return jsonify({"error": f"ไม่สามารถโหลดรูปภาพได้: {str(e)}"}), 400
        
        # สร้าง drawing context
        draw = ImageDraw.Draw(img)
        
        # แก้ไขข้อความภาษาไทย
        fixed_text = fix_thai_text(text)
        
        # หาฟอนต์
        font = get_thai_font(font_size)
        
        # เพิ่มข้อความ (รองรับหลายบรรทัด)
        lines = fixed_text.split('\n')
        current_y = y
        
        for line in lines:
            if line.strip():  # ข้ามบรรทัดว่าง
                add_text_with_stroke(
                    draw=draw,
                    text=line,
                    position=(x, current_y),
                    font=font,
                    fill_color=font_color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width
                )
            current_y += font_size + 10  # เว้นระยะระหว่างบรรทัด
        
        # บันทึกและส่งกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=95, optimize=True)
        img_io.seek(0)
        
        return send_file(
            img_io, 
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='result.jpg'
        )
        
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)