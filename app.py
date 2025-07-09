import os
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "API is running!",
        "how_to_use": "POST to /text-on-image with JSON data"
    })

@app.route('/text-on-image', methods=['POST'])
def text_on_image():
    try:
        # รับข้อมูล
        data = request.get_json()
        
        # ดาวน์โหลดรูป
        img_url = data.get('img_url')
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))
        
        # เตรียมวาดข้อความ
        draw = ImageDraw.Draw(img)
        text = data.get('text', 'Hello')
        x = int(data.get('x', 50))
        y = int(data.get('y', 50))
        
        # พยายามใช้ฟอนต์ไทย
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/thai/Garuda.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # วาดข้อความ
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # ส่งรูปกลับ
        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        
        return send_file(output, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)