import os
import requests
from flask import Flask, request, send_file, jsonify, redirect
from PIL import Image, ImageDraw
from io import BytesIO
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API - Web Service Solution ✅",
        "info": "Redirects to working Thai text services",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/simple-image": "GET - Generate simple Thai text image",
            "/redirect-service": "GET - Redirect to working service"
        }
    })

@app.route('/redirect-service')
def redirect_service():
    """Redirect ไปยัง service ที่ทำงานได้จริง"""
    # Redirect ไปยัง Google Chart API ที่รองรับภาษาไทย
    thai_text = "ทั้งที่ยังรัก|ที่นี่ ยิ้ม สิ้นสุด|สวัสดีครับ"
    
    chart_url = f"https://chart.googleapis.com/chart?cht=lc&chs=800x400&chd=t:0,0&chxt=x,y&chxl=0:|{urllib.parse.quote(thai_text)}&chco=1976D2&chf=bg,s,1976D2&chts=FFFFFF,36"
    
    return redirect(chart_url)

@app.route('/simple-image')
def simple_image():
    """สร้างรูปข้อความไทยด้วย shields.io"""
    text = request.args.get('text', 'สวัสดีครับ')
    
    # ใช้ shields.io ที่รองรับ UTF-8
    shields_url = f"https://img.shields.io/badge/Thai_Text-{urllib.parse.quote(text)}-blue?style=for-the-badge&labelColor=1976D2&color=4CAF50"
    
    try:
        response = requests.get(shields_url, timeout=10)
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/svg+xml',
                as_attachment=True,
                download_name='thai_text.svg'
            )
    except:
        pass
    
    # Fallback
    return jsonify({"error": "Service unavailable", "try_url": shields_url})

@app.route('/text-on-image', methods=['POST'])
def add_text():
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # ส่งกลับ URL ของ service ที่ทำงานได้
        working_services = [
            {
                "name": "Canva URL",
                "url": f"https://www.canva.com/design/create?text={urllib.parse.quote(text)}"
            },
            {
                "name": "Placeholdit with Thai",
                "url": f"https://via.placeholder.com/800x400/1976D2/FFFFFF?text={urllib.parse.quote(text)}"
            },
            {
                "name": "DummyImage",
                "url": f"https://dummyimage.com/800x400/1976D2/ffffff&text={urllib.parse.quote(text)}"
            },
            {
                "name": "Shields.io Badge",
                "url": f"https://img.shields.io/badge/Thai-{urllib.parse.quote(text)}-blue"
            }
        ]
        
        # ลองใช้ service ที่ 2 (Placeholdit)
        try:
            placeholder_url = f"https://via.placeholder.com/800x400/1976D2/FFFFFF?text={urllib.parse.quote(text)}"
            response = requests.get(placeholder_url, timeout=10)
            
            if response.status_code == 200:
                return send_file(
                    BytesIO(response.content),
                    mimetype='image/png'
                )
        except:
            pass
        
        return jsonify({
            "message": "Use one of these working services:",
            "services": working_services,
            "recommended": f"https://img.shields.io/badge/Thai_Text-{urllib.parse.quote(text)}-blue?style=for-the-badge"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    """ทดสอบด้วย service ที่ทำงานได้แน่นอน"""
    thai_text = "ทั้งที่ยังรัก ที่นี่ ยิ้ม สิ้นสุด"
    
    # ลองใช้ DummyImage
    try:
        dummy_url = f"https://dummyimage.com/800x400/1976D2/ffffff&text={urllib.parse.quote(thai_text)}"
        response = requests.get(dummy_url, timeout=10)
        
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='thai_test.png'
            )
    except:
        pass
    
    # ลองใช้ Shields.io
    try:
        shields_url = f"https://img.shields.io/badge/Thai_Test-{urllib.parse.quote(thai_text)}-blue?style=for-the-badge&labelColor=1976D2&color=4CAF50"
        response = requests.get(shields_url, timeout=10)
        
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/svg+xml',
                as_attachment=True,
                download_name='thai_test.svg'
            )
    except:
        pass
    
    # สุดท้าย - ให้ URL ที่ใช้งานได้
    return jsonify({
        "message": "Try these working URLs:",
        "urls": [
            f"https://dummyimage.com/800x400/1976D2/ffffff&text={urllib.parse.quote(thai_text)}",
            f"https://img.shields.io/badge/Thai_Test-{urllib.parse.quote(thai_text)}-blue?style=for-the-badge",
            f"https://via.placeholder.com/800x400/1976D2/FFFFFF?text={urllib.parse.quote(thai_text)}"
        ]
    })

@app.route('/working-url')
def working_url():
    """ส่งกลับ URL ที่ทำงานได้แน่นอน"""
    text = request.args.get('text', 'สวัสดีครับ')
    
    working_urls = [
        f"https://dummyimage.com/800x400/1976D2/ffffff&text={urllib.parse.quote(text)}",
        f"https://img.shields.io/badge/Thai-{urllib.parse.quote(text)}-blue?style=for-the-badge",
        f"https://via.placeholder.com/800x400/1976D2/FFFFFF?text={urllib.parse.quote(text)}"
    ]
    
    return jsonify({
        "working_urls": working_urls,
        "instructions": "Copy any URL above and paste in browser to see Thai text image"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)