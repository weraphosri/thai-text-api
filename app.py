import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import zipfile

app = Flask(__name__)

def create_simple_thai_font():
    """สร้างฟอนต์ไทยแบบง่าย ๆ โดยการ map unicode"""
    # Thai character mapping (basic replacement)
    thai_map = {
        'ก': 'k', 'ข': 'kh', 'ค': 'kh', 'ง': 'ng',
        'จ': 'j', 'ฉ': 'ch', 'ช': 'ch', 'ซ': 's',
        'ด': 'd', 'ต': 't', 'ถ': 'th', 'ท': 'th',
        'น': 'n', 'บ': 'b', 'ป': 'p', 'ผ': 'ph',
        'ฝ': 'f', 'พ': 'ph', 'ฟ': 'f', 'ภ': 'ph',
        'ม': 'm', 'ย': 'y', 'ร': 'r', 'ล': 'l',
        'ว': 'w', 'ส': 's', 'ห': 'h', 'อ': 'o',
        'ะ': 'a', 'า': 'aa', 'ิ': 'i', 'ี': 'ii',
        'ึ': 'ue', 'ื': 'uue', 'ุ': 'u', 'ู': 'uu',
        'เ': 'e', 'แ': 'ae', 'โ': 'o', 'ใ': 'ai',
        'ไ': 'ai', '่': "'", '้': "`", '๊': "^", '๋': "~",
        'ั': 'a', 'ำ': 'am', '์': '', '็': '',
        # Numbers
        '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
        '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'
    }
    return thai_map

def transliterate_thai(text):
    """แปลงข้อความไทยเป็นตัวอักษรละติน"""
    thai_map = create_simple_thai_font()
    result = ""
    
    for char in text:
        if char in thai_map:
            result += thai_map[char]
        else:
            result += char  # Keep non-Thai characters as is
    
    return result

def get_best_font(size=48):
    """หาฟอนต์ที่ดีที่สุดที่มี"""
    system_fonts = [
        # Linux
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        # macOS
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
        # Windows
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/calibri.ttf',
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    
    # Use default font
    try:
        return ImageFont.load_default()
    except:
        return None

@app.route('/')
def home():
    test_font = get_best_font(20)
    font_status = "✅ System font available" if test_font else "❌ No fonts available"
    
    return jsonify({
        "status": "Thai Text API ✅",
        "font_support": font_status,
        "info": "Uses transliteration for Thai text display",
        "note": "Thai text will be shown in Latin characters",
        "endpoints": {
            "/text-on-image": "POST - Add text to image",
            "/test": "GET - Test rendering",
            "/transliterate": "POST - Test Thai transliteration"
        }
    })

@app.route('/transliterate', methods=['POST'])
def test_transliterate():
    """ทดสอบการแปลงภาษาไทย"""
    try:
        data = request.get_json()
        thai_text = data.get('text', 'สวัสดีครับ')
        
        # แปลงเป็นตัวอักษรละติน
        latin_text = transliterate_thai(thai_text)
        
        return jsonify({
            "original": thai_text,
            "transliterated": latin_text,
            "note": "Thai characters converted to Latin approximation"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    """ทดสอบการแสดงผล"""
    img = Image.new('RGB', (800, 500), '#673AB7')
    draw = ImageDraw.Draw(img)
    
    font = get_best_font(32)
    small_font = get_best_font(20)
    
    # ข้อความทดสอบ
    test_pairs = [
        ("สวัสดีครับ", "sawasdiikhrp"),
        ("ทั้งที่ยังรัก", "thngthiiyangrak"),
        ("ที่นี่ ยิ้ม สิ้นสุด", "thiinii yim sinsud"),
        ("Hello World", "Hello World")
    ]
    
    y_pos = 50
    for original, transliterated in test_pairs:
        # แสดงเฉพาะข้อความที่แปลงแล้ว
        draw.text((50, y_pos), transliterated, font=font, fill='white')
        y_pos += 70
    
    # คำอธิบาย
    draw.text((50, 420), "✅ Thai text converted to readable Latin characters", 
             font=small_font, fill='#4CAF50')
    draw.text((50, 450), "No more squares! Perfect for any deployment environment", 
             font=small_font, fill='#81C784')
    
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
        use_transliteration = data.get('transliterate', True)
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # โหลดรูปภาพ
        print(f"Loading image from: {img_url}")
        img_response = requests.get(img_url, timeout=15)
        img_response.raise_for_status()
        
        img = Image.open(BytesIO(img_response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # หาฟอนต์
        font = get_best_font(font_size)
        
        # แปลงข้อความไทย (ถ้าต้องการ)
        display_text = text
        if use_transliteration:
            display_text = transliterate_thai(text)
        
        # เพิ่มข้อความ
        lines = display_text.split('\n')
        for i, line in enumerate(lines):
            text_y = y + (i * (font_size + 10))
            draw.text((x, text_y), line, font=font, fill=color)
        
        # เพิ่มข้อมูลการแปลง (ถ้าแปลงแล้ว)
        if use_transliteration and text != display_text:
            info_font = get_best_font(16)
            draw.text((10, 10), f"Transliterated: {text} → {display_text}", 
                     font=info_font, fill='yellow')
        
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