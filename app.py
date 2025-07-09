import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "Using external Thai text service for perfect rendering",
        "endpoints": {
            "/text-on-image": "POST - เพิ่มข้อความไทยบนรูป",
            "/test": "GET - ทดสอบการทำงาน"
        }
    })

@app.route('/test')
def test():
    """ทดสอบด้วย IMGBun API"""
    try:
        # สร้างข้อความทดสอบ
        test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
        
        # เรียกใช้ IMGBun API
        imgbun_url = "https://imgbun.com/api/text_to_image"
        params = {
            'text': test_text,
            'font_size': 36,
            'font_color': 'white',
            'bg_color': '#1976D2',
            'width': 800,
            'height': 400,
            'format': 'jpeg'
        }
        
        response = requests.get(imgbun_url, params=params, timeout=10)
        
        if response.status_code == 200:
            return send_file(BytesIO(response.content), mimetype='image/jpeg')
        else:
            # Fallback: สร้างรูปง่ายๆ
            img = Image.new('RGB', (800, 400), '#1976D2')
            draw = ImageDraw.Draw(img)
            draw.text((50, 180), "IMGBun API not available", fill='white')
            
            img_io = BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')
            
    except Exception as e:
        # สร้างรูป error
        img = Image.new('RGB', (800, 400), '#F44336')
        draw = ImageDraw.Draw(img)
        draw.text((50, 180), f"Error: {str(e)}", fill='white')
        
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
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
        
        # วิธีที่ 1: ใช้ IMGBun สำหรับสร้างข้อความ
        try:
            # สร้างรูปข้อความด้วย IMGBun
            imgbun_url = "https://imgbun.com/api/text_to_image"
            text_params = {
                'text': text,
                'font_size': font_size,
                'font_color': color.replace('#', ''),
                'bg_color': 'transparent',
                'format': 'png'
            }
            
            text_response = requests.get(imgbun_url, params=text_params, timeout=10)
            
            if text_response.status_code == 200:
                # โหลดรูปหลัก
                img_response = requests.get(img_url, timeout=10)
                main_img = Image.open(BytesIO(img_response.content)).convert('RGBA')
                
                # โหลดรูปข้อความ
                text_img = Image.open(BytesIO(text_response.content)).convert('RGBA')
                
                # รวมรูป
                main_img.paste(text_img, (x, y), text_img)
                
                # ส่งกลับ
                result = main_img.convert('RGB')
                img_io = BytesIO()
                result.save(img_io, 'JPEG', quality=90)
                img_io.seek(0)
                
                return send_file(img_io, mimetype='image/jpeg')
                
        except Exception as imgbun_error:
            print(f"IMGBun error: {imgbun_error}")
        
        # วิธีที่ 2: Fallback - ใช้ PIL ธรรมดา
        img_response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(img_response.content)).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # ใช้ฟอนต์ default
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        for i, line in enumerate(lines):
            draw.text((x, y + i * (font_size + 5)), line, font=font, fill=color)
        
        # เพิ่มคำเตือน
        draw.text((10, 10), "⚠️ Basic rendering (may not display Thai correctly)", 
                 fill='red', font=font)
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/imgbun-direct', methods=['POST'])
def imgbun_direct():
    """เรียกใช้ IMGBun โดยตรง"""
    try:
        data = request.get_json()
        text = data.get('text', 'Hello')
        
        # เรียก IMGBun API
        imgbun_url = "https://imgbun.com/api/text_to_image"
        params = {
            'text': text,
            'font_size': data.get('font_size', 48),
            'font_color': data.get('font_color', 'white').replace('#', ''),
            'bg_color': data.get('bg_color', '1976D2').replace('#', ''),
            'width': data.get('width', 800),
            'height': data.get('height', 400),
            'format': 'jpeg'
        }
        
        response = requests.get(imgbun_url, params=params, timeout=15)
        
        if response.status_code == 200:
            return send_file(BytesIO(response.content), mimetype='image/jpeg')
        else:
            return jsonify({"error": "IMGBun service unavailable"}), 503
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)