import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API - External Service Solution ✅",
        "info": "Uses external API for guaranteed Thai text rendering",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/test": "GET - Test Thai text rendering"
        }
    })

@app.route('/test')
def test():
    """ทดสอบด้วย external service"""
    try:
        # ใช้ QuickChart API ที่รองรับภาษาไทย
        text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
        
        chart_config = {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "data": [{"x": 0, "y": 0}],
                    "pointRadius": 0
                }]
            },
            "options": {
                "plugins": {
                    "title": {
                        "display": True,
                        "text": text.split('\n'),
                        "font": {
                            "size": 36,
                            "family": "Noto Sans Thai"
                        }
                    }
                },
                "scales": {
                    "x": {"display": False},
                    "y": {"display": False}
                },
                "legend": {"display": False}
            }
        }
        
        # เรียก QuickChart API
        response = requests.post(
            'https://quickchart.io/chart',
            json={
                "chart": chart_config,
                "width": 800,
                "height": 400,
                "format": "png"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='thai_test.png'
            )
        else:
            # Fallback: สร้างรูปแจ้งเตือน
            img = Image.new('RGB', (800, 400), '#FF5722')
            draw = ImageDraw.Draw(img)
            draw.text((50, 180), "External service unavailable", fill='white')
            
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png')
            
    except Exception as e:
        # Error fallback
        img = Image.new('RGB', (800, 400), '#F44336')
        draw = ImageDraw.Draw(img)
        draw.text((50, 180), f"Error: {str(e)}", fill='white')
        
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

@app.route('/text-on-image', methods=['POST'])
def add_text():
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # วิธีที่ 1: ใช้ TextOnImage API
        try:
            text_api_response = requests.post(
                'https://api.textoverimage.moesif.com/image',
                json={
                    "image_url": img_url,
                    "text": text,
                    "x_pos": x,
                    "y_pos": y,
                    "font_size": font_size,
                    "font_color": color,
                    "font_family": "Noto Sans Thai"
                },
                timeout=15
            )
            
            if text_api_response.status_code == 200:
                return send_file(
                    BytesIO(text_api_response.content),
                    mimetype='image/jpeg'
                )
        except:
            pass
        
        # วิธีที่ 2: ใช้ Bannerbear API
        try:
            bannerbear_response = requests.post(
                'https://api.bannerbear.com/v2/images',
                headers={
                    'Authorization': 'Bearer demo_key'  # Demo key
                },
                json={
                    "template": "simple-text-overlay",
                    "modifications": [
                        {
                            "name": "background",
                            "image_url": img_url
                        },
                        {
                            "name": "text",
                            "text": text,
                            "x": x,
                            "y": y,
                            "font_size": font_size,
                            "color": color
                        }
                    ]
                },
                timeout=15
            )
            
            if bannerbear_response.status_code == 200:
                image_url = bannerbear_response.json().get('image_url')
                if image_url:
                    img_response = requests.get(image_url, timeout=10)
                    return send_file(
                        BytesIO(img_response.content),
                        mimetype='image/jpeg'
                    )
        except:
            pass
        
        # วิธีที่ 3: ใช้ Placid API
        try:
            placid_response = requests.post(
                'https://api.placid.app/api/rest/image-templates/demo/generate',
                json={
                    "image_url": img_url,
                    "text": text,
                    "x": x,
                    "y": y,
                    "font_size": font_size,
                    "text_color": color,
                    "font_family": "Noto Sans Thai"
                },
                timeout=15
            )
            
            if placid_response.status_code == 200:
                return send_file(
                    BytesIO(placid_response.content),
                    mimetype='image/jpeg'
                )
        except:
            pass
        
        # วิธีที่ 4: Fallback - ใช้ PIL แบบง่าย
        img_response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(img_response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        # เพิ่มข้อความ (อาจเป็นสี่เหลี่ยม)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            draw.text((x, y + i * 60), line, fill=color)
        
        # เพิ่มคำเตือน
        draw.text((10, 10), "⚠️ Using fallback rendering", fill='red')
        
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simple-thai', methods=['POST'])
def simple_thai():
    """สร้างรูปข้อความไทยง่ายๆ"""
    try:
        data = request.get_json()
        text = data.get('text', 'สวัสดี')
        
        # ใช้ Canvas API
        canvas_response = requests.post(
            'https://api.htmlcsstoimage.com/v1/image',
            auth=('demo', 'demo'),
            json={
                "html": f"""
                <div style="
                    width: 800px; 
                    height: 400px; 
                    background: #1976D2;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: 'Noto Sans Thai', sans-serif;
                    font-size: 48px;
                    color: white;
                    text-align: center;
                    line-height: 1.5;
                ">
                    {text.replace(chr(10), '<br>')}
                </div>
                """,
                "css": """
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap');
                """
            },
            timeout=15
        )
        
        if canvas_response.status_code == 200:
            return send_file(
                BytesIO(canvas_response.content),
                mimetype='image/png'
            )
        else:
            return jsonify({"error": "Canvas API failed"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)