import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import logging

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "API is running! ✅",
        "endpoints": {
            "/": "This page",
            "/text-on-image": "POST - Add text to image",
            "/test": "GET - Test image generation"
        },
        "example": {
            "url": "/text-on-image",
            "method": "POST",
            "body": {
                "img_url": "https://picsum.photos/800/600",
                "text": "Hello ทดสอบ",
                "x": 100,
                "y": 100
            }
        }
    })

@app.route('/test')
def test_image():
    """Test endpoint - สร้างรูปทดสอบ"""
    # สร้างรูปเปล่า
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # วาดข้อความ
    text = "Test Image - ทดสอบภาษาไทย"
    draw.text((50, 50), text, fill='black')
    
    # ส่งกลับ
    output = BytesIO()
    img.save(output, format='JPEG', quality=90)
    output.seek(0)
    
    return send_file(output, mimetype='image/jpeg')

@app.route('/text-on-image', methods=['POST'])
def text_on_image():
    try:
        # Log incoming request
        logger.info("Received request to /text-on-image")
        
        # รับข้อมูล JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        logger.info(f"Request data: {data}")
        
        # ตรวจสอบ required fields
        img_url = data.get('img_url')
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # รับค่าอื่นๆ
        text = data.get('text', 'Hello World')
        x = int(data.get('x', 50))
        y = int(data.get('y', 50))
        font_size = int(data.get('font_size', 48))
        font_color = data.get('font_color', '#FFFFFF')
        
        logger.info(f"Processing: text='{text}', position=({x},{y})")
        
        # ดาวน์โหลดรูป
        logger.info(f"Downloading image from: {img_url}")
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        
        # เปิดรูป
        img = Image.open(BytesIO(response.content))
        logger.info(f"Image size: {img.size}")
        
        # แปลงเป็น RGB ถ้าจำเป็น
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # วาดข้อความ
        draw = ImageDraw.Draw(img)
        
        # พยายามโหลดฟอนต์ไทย
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/thai/TlwgMono.ttf",
            "/usr/share/fonts/truetype/thai/Garuda.ttf",
            "/usr/share/fonts/truetype/thai/Kinnari.ttf",
            "/usr/share/fonts/truetype/thai/Loma.ttf",
            "/usr/share/fonts/truetype/thai/Norasi.ttf",
            "/usr/share/fonts/truetype/thai/Purisa.ttf",
            "/usr/share/fonts/truetype/thai/Sawasdee.ttf",
            "/usr/share/fonts/truetype/thai/TlwgTypewriter.ttf",
            "/usr/share/fonts/truetype/thai/TlwgTypo.ttf",
            "/usr/share/fonts/truetype/thai/Umpush.ttf",
            "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                logger.info(f"Loaded font: {font_path}")
                break
            except:
                continue
        
        if not font:
            logger.warning("No Thai font found, using default")
            font = ImageFont.load_default()
        
        # แปลงสีจาก hex
        try:
            if font_color.startswith('#'):
                font_color = font_color[1:]
            r = int(font_color[0:2], 16)
            g = int(font_color[2:4], 16)
            b = int(font_color[4:6], 16)
            color = (r, g, b)
        except:
            color = (255, 255, 255)
        
        # วาดเงาก่อน
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, 
                  font=font, fill=(0, 0, 0))
        
        # วาดข้อความหลัก
        draw.text((x, y), text, font=font, fill=color)
        
        # บันทึกและส่งกลับ
        output = BytesIO()
        img.save(output, format='JPEG', quality=90)
        output.seek(0)
        
        logger.info("Successfully generated image")
        return send_file(output, mimetype='image/jpeg', as_attachment=False)
        
    except Exception as e:
        logger.error(f"Error in text_on_image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Failed to process image",
            "detail": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)