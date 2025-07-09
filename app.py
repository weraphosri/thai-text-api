import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import urllib.parse

app = Flask(__name__)

def get_basic_font(size=48):
    """ใช้ฟอนต์พื้นฐานที่รองรับภาษาไทย"""
    try:
        # ลองใช้ฟอนต์ในระบบ
        system_fonts = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/System/Library/Fonts/Arial.ttf',  # macOS
            'C:/Windows/Fonts/arial.ttf',  # Windows
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # ใช้ default
        return ImageFont.load_default()
        
    except:
        return ImageFont.load_default()

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "Simple and reliable Thai text on images",
        "endpoints": {
            "/text-on-image": "POST - เพิ่มข้อความบนรูป",
            "/test": "GET - ทดสอบการทำงาน",
            "/simple-text": "POST - สร้างรูปข้อความธรรมดา"
        },
        "example": {
            "method": "POST",
            "url": "/text-on-image",
            "body": {
                "img_url": "https://picsum.photos/800/600",
                "text": "ทดสอบภาษาไทย",
                "x": 100,
                "y": 100,
                "font_size": 48,
                "font_color": "#FFFFFF"
            }
        }
    })

@app.route('/test')
def test():
    """ทดสอบสร้างรูปพื้นฐาน"""
    try:
        # สร้างรูปพื้นฐาน
        img = Image.new('RGB', (800, 400), color='#2196F3')
        draw = ImageDraw.Draw(img)
        
        # ข้อความทดสอบ
        font = get_basic_font(32)
        
        # เขียนข้อความ (อาจจะเป็นสี่เหลี่ยม แต่ไฟล์จะเปิดได้)
        draw.text((50, 50), "Thai Text Test", font=font, fill='white')
        draw.text((50, 100), "ทดสอบภาษาไทย", font=font, fill='white')
        draw.text((50, 150), "Hello World", font=font, fill='white')
        
        # ข้อความสถานะ
        status_font = get_basic_font(20)
        draw.text((50, 300), "✅ Image generated successfully", font=status_font, fill='#4CAF50')
        draw.text((50, 330), "Thai text may show as squares (font limitation)", font=status_font, fill='#FF9800')
        
        # บันทึกและส่งกลับ
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        return send_file(
            img_buffer,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name='test.jpg'
        )
        
    except Exception as e:
        return jsonify({"error": f"Test failed: {str(e)}"}), 500

@app.route('/simple-text', methods=['POST'])
def simple_text():
    """สร้างรูปข้อความธรรมดา"""
    try:
        data = request.get_json()
        
        text = data.get('text', 'Hello')
        width = int(data.get('width', 800))
        height = int(data.get('height', 400))
        bg_color = data.get('bg_color', '#2196F3')
        font_color = data.get('font_color', '#FFFFFF')
        font_size = int(data.get('font_size', 48))
        
        # สร้างรูป
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # เขียนข้อความ
        font = get_basic_font(font_size)
        lines = text.split('\n')
        
        y_pos = 50
        for line in lines:
            draw.text((50, y_pos), line, font=font, fill=font_color)
            y_pos += font_size + 10
        
        # บันทึกและส่งกลับ
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        return send_file(
            img_buffer,
            mimetype='image/jpeg',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({"error": f"Simple text failed: {str(e)}"}), 500

@app.route('/text-on-image', methods=['POST'])
def add_text():
    """เพิ่มข้อความบนรูป"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 50))
        y = int(data.get('y', 50))
        font_size = int(data.get('font_size', 48))
        font_color = data.get('font_color', '#FFFFFF')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # โหลดรูปหลัก
        try:
            print(f"Loading image from: {img_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            img_response = requests.get(img_url, headers=headers, timeout=15)
            img_response.raise_for_status()
            
            # เปิดรูป
            img = Image.open(BytesIO(img_response.content))
            
            # แปลงเป็น RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            print(f"Image loaded successfully: {img.size}")
            
        except Exception as e:
            return jsonify({"error": f"Failed to load image: {str(e)}"}), 400
        
        # เพิ่มข้อความ
        draw = ImageDraw.Draw(img)
        font = get_basic_font(font_size)
        
        # เขียนข้อความทีละบรรทัด
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            if line.strip():
                draw.text((x, current_y), line, font=font, fill=font_color)
                current_y += font_size + 5
        
        # บันทึกและส่งกลับ
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=85, optimize=True)
        img_buffer.seek(0)
        
        print(f"Image processed successfully, size: {img_buffer.getbuffer().nbytes} bytes")
        
        return send_file(
            img_buffer,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='result.jpg'
        )
        
    except Exception as e:
        print(f"Error in add_text: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/health')
def health():
    """ตรวจสอบสถานะ API"""
    return jsonify({
        "status": "healthy",
        "message": "API is running normally"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)