import os
from flask import Flask, request, send_file, jsonify, redirect
from io import BytesIO
import requests
import urllib.parse
import base64

app = Flask(__name__)

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dtuz1nors')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '992211531151382')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', 'gRAksjdUhdLW_LIjgYBeZNwtPd4')

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "Using Cloudinary for real image output with Thai text support",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image (returns PNG/JPG)",
            "/test": "GET - Test Thai rendering",
            "/cloudinary-url": "POST - Get Cloudinary URL for image with text"
        }
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    # ใช้ Cloudinary demo account
    base_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch"
    
    # รูปตัวอย่าง
    sample_image = "https://picsum.photos/800/600"
    
    # Text overlay
    text = "ทั้งที่ยังรัก"
    font_family = "Noto Sans Thai"  # Cloudinary รองรับ Google Fonts
    font_size = 60
    
    # สร้าง text overlay transformation
    text_overlay = f"l_text:{font_family}_{font_size}:{urllib.parse.quote(text)},co_rgb:FFFFFF,g_center"
    
    # สร้าง URL สุดท้าย
    final_url = f"{base_url}/{text_overlay}/{urllib.parse.quote(sample_image)}"
    
    # Download และส่งกลับเป็นไฟล์
    response = requests.get(final_url)
    if response.status_code == 200:
        return send_file(
            BytesIO(response.content),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='test_thai.jpg'
        )
    else:
        return jsonify({"error": "Failed to generate image"}), 500

@app.route('/text-on-image', methods=['POST'])
def add_text():
    """เพิ่มข้อความบนรูป - ส่งกลับเป็นรูปภาพจริง (PNG/JPG)"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 0))  # Cloudinary ใช้ offset จาก center
        y = int(data.get('y', 0))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF').replace('#', '')
        align = data.get('align', 'center')
        valign = data.get('valign', 'middle')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # แปลง alignment เป็น Cloudinary gravity
        gravity_map = {
            ('left', 'top'): 'north_west',
            ('center', 'top'): 'north',
            ('right', 'top'): 'north_east',
            ('left', 'middle'): 'west',
            ('center', 'middle'): 'center',
            ('right', 'middle'): 'east',
            ('left', 'bottom'): 'south_west',
            ('center', 'bottom'): 'south',
            ('right', 'bottom'): 'south_east'
        }
        gravity = gravity_map.get((align, valign), 'center')
        
        # ถ้ามีหลายบรรทัด
        if '\n' in text:
            # สร้าง text overlay สำหรับแต่ละบรรทัด
            lines = text.split('\n')
            overlays = []
            for i, line in enumerate(lines):
                line_y = y + (i * int(font_size * 1.2))
                overlay = f"l_text:Noto Sans Thai_{font_size}:{urllib.parse.quote(line)},co_rgb:{color},g_{gravity},x_{x},y_{line_y}"
                overlays.append(overlay)
            text_overlay = '/'.join(overlays)
        else:
            # บรรทัดเดียว
            text_overlay = f"l_text:Noto Sans Thai_{font_size}:{urllib.parse.quote(text)},co_rgb:{color},g_{gravity},x_{x},y_{y}"
        
        # สร้าง Cloudinary URL
        base_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch"
        final_url = f"{base_url}/{text_overlay}/{urllib.parse.quote(img_url)}"
        
        # Download รูปและส่งกลับ
        response = requests.get(final_url)
        if response.status_code == 200:
            # ตรวจสอบ content type
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            extension = 'jpg' if 'jpeg' in content_type else 'png'
            
            return send_file(
                BytesIO(response.content),
                mimetype=content_type,
                as_attachment=True,
                download_name=f'result.{extension}'
            )
        else:
            return jsonify({
                "error": "Failed to generate image",
                "cloudinary_url": final_url,
                "status_code": response.status_code
            }), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cloudinary-url', methods=['POST'])
def get_cloudinary_url():
    """สร้าง Cloudinary URL สำหรับ n8n หรือการใช้งานอื่นๆ"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF').replace('#', '')
        align = data.get('align', 'center')
        valign = data.get('valign', 'middle')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # แปลง alignment
        gravity_map = {
            ('left', 'top'): 'north_west',
            ('center', 'top'): 'north',
            ('right', 'top'): 'north_east',
            ('left', 'middle'): 'west',
            ('center', 'middle'): 'center',
            ('right', 'middle'): 'east',
            ('left', 'bottom'): 'south_west',
            ('center', 'bottom'): 'south',
            ('right', 'bottom'): 'south_east'
        }
        gravity = gravity_map.get((align, valign), 'center')
        
        # สร้าง text overlay
        text_overlay = f"l_text:Noto Sans Thai_{font_size}:{urllib.parse.quote(text)},co_rgb:{color},g_{gravity},x_{x},y_{y}"
        
        # สร้าง URL
        base_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/fetch"
        final_url = f"{base_url}/{text_overlay}/{urllib.parse.quote(img_url)}"
        
        return jsonify({
            "success": True,
            "cloudinary_url": final_url,
            "direct_download": f"{final_url}?dl=true",
            "parameters": {
                "text": text,
                "position": f"{align} {valign}",
                "offset": f"x:{x}, y:{y}",
                "font_size": font_size,
                "color": f"#{color}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-and-transform', methods=['POST'])
def upload_and_transform():
    """อัพโหลดรูปไป Cloudinary แล้วใส่ข้อความ (ต้องมี API credentials)"""
    if not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        return jsonify({
            "error": "Cloudinary API credentials not configured",
            "info": "Please set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET environment variables"
        }), 400
    
    try:
        data = request.get_json()
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # Upload to Cloudinary
        upload_url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"
        
        # สร้าง transformation
        transformation = f"l_text:Noto Sans Thai_48:{urllib.parse.quote(text)},co_rgb:FFFFFF,g_center"
        
        # Upload parameters
        params = {
            'file': img_url,
            'upload_preset': 'unsigned',  # ต้องสร้าง unsigned preset ใน Cloudinary dashboard
            'transformation': transformation
        }
        
        # Basic auth
        auth = (CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
        
        response = requests.post(upload_url, data=params, auth=auth)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "success": True,
                "url": result['secure_url'],
                "public_id": result['public_id']
            })
        else:
            return jsonify({"error": "Upload failed", "details": response.text}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)