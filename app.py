import os
from flask import Flask, request, send_file, jsonify, redirect
from io import BytesIO
import requests
import urllib.parse
import json
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "Simple working solution for Thai text on images",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/test": "GET - Test Thai rendering",
            "/simple": "GET - Simple text image",
            "/get-html": "POST - Get HTML for n8n HTML to Image node",
            "/get-html-raw": "POST - Get raw HTML"
        }
    })

@app.route('/test')
def test():
    """ทดสอบการแสดงผลภาษาไทย"""
    # ใช้ QuickChart.io ที่รองรับภาษาไทยและ Unicode
    text = "ทั้งที่ยังรัก"
    
    chart_config = {
        "chart": {
            "type": "radialGauge",
            "data": {
                "datasets": [{
                    "data": [0],
                    "backgroundColor": "transparent"
                }]
            },
            "options": {
                "centerArea": {
                    "text": text,
                    "fontSize": 48,
                    "fontColor": "#FFFFFF",
                    "fontFamily": "Noto Sans Thai"
                },
                "backgroundColor": "#1976D2"
            }
        },
        "width": 800,
        "height": 600
    }
    
    # URL encode the config
    encoded_config = urllib.parse.quote(json.dumps(chart_config))
    quickchart_url = f"https://quickchart.io/chart?c={encoded_config}"
    
    # Fallback to simple method
    # ใช้ placeholder service ที่รองรับ Unicode
    simple_url = f"https://via.placeholder.com/800x600/1976D2/FFFFFF?text={urllib.parse.quote(text)}"
    
    # ลองดึงรูปจาก placeholder ก่อน
    try:
        response = requests.get(simple_url, timeout=10)
        if response.status_code == 200 and len(response.content) > 1000:
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='test_thai.png'
            )
    except:
        pass
    
    # ถ้าไม่ได้ ใช้ QuickChart
    return redirect(quickchart_url)

@app.route('/simple')
def simple():
    """สร้างรูปง่ายๆ พร้อมข้อความ"""
    text = request.args.get('text', 'สวัสดี')
    bg = request.args.get('bg', '1976D2')
    color = request.args.get('color', 'FFFFFF')
    
    # ใช้ dummyimage.com
    url = f"https://dummyimage.com/800x600/{bg}/{color}.png&text={urllib.parse.quote(text)}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='simple.png'
            )
    except:
        pass
    
    # Fallback
    return redirect(url)

@app.route('/text-on-image', methods=['POST'])
def add_text():
    """เพิ่มข้อความบนรูป - ส่งกลับเป็น PNG ผ่าน external service"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        align = data.get('align', 'left')
        valign = data.get('valign', 'top')
        output_format = data.get('format', 'svg')  # svg หรือ png
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # สร้าง SVG
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
        text-anchor: {'middle' if align == 'center' else 'start'};
        dominant-baseline: {'central' if valign == 'middle' else 'hanging'};
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
  <text x="{x}" y="{y}" class="thai-text">{text}</text>
</svg>'''
        
        # ถ้าต้องการ PNG ใช้ CloudConvert API (ฟรี 25 ครั้ง/วัน)
        if output_format == 'png':
            try:
                # CloudConvert API
                cloudconvert_url = "https://api.cloudconvert.com/v2/convert"
                
                # หรือใช้ svg2png.com API
                svg_base64 = BytesIO(svg_content.encode('utf-8')).read().hex()
                png_api_url = f"https://svg2png.com/api/convert?svg={svg_base64}"
                
                response = requests.get(png_api_url, timeout=10)
                if response.status_code == 200:
                    return send_file(
                        BytesIO(response.content),
                        mimetype='image/png',
                        as_attachment=True,
                        download_name='result.png'
                    )
            except:
                pass
        
        # Default: ส่ง SVG
        return send_file(
            BytesIO(svg_content.encode('utf-8')),
            mimetype='image/svg+xml',
            as_attachment=True,
            download_name='result.svg'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text-on-image-base64', methods=['POST'])
def add_text_base64():
    """เพิ่มข้อความบนรูป - ส่งกลับเป็น base64 data URL"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        align = data.get('align', 'left')
        valign = data.get('valign', 'top')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # สร้าง SVG
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: {color};
        text-anchor: {'middle' if align == 'center' else 'start'};
        dominant-baseline: {'central' if valign == 'middle' else 'hanging'};
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
  <text x="{x}" y="{y}" class="thai-text">{text}</text>
</svg>'''
        
        # แปลงเป็น base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        data_url = f"data:image/svg+xml;base64,{svg_base64}"
        
        return jsonify({
            "success": True,
            "data_url": data_url,
            "svg_base64": svg_base64,
            "format": "svg",
            "note": "Use this data URL in HTML img tag or convert with other tools"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/html-preview', methods=['POST'])
def html_preview():
    """สร้าง HTML preview"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url', 'https://picsum.photos/800/600')
        text = data.get('text', 'ทดสอบ')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{ margin: 0; font-family: 'Noto Sans Thai', sans-serif; }}
                .container {{
                    width: 800px;
                    height: 600px;
                    position: relative;
                    background: url('{img_url}') center/cover;
                }}
                .text {{
                    position: absolute;
                    left: {x}px;
                    top: {y}px;
                    color: {color};
                    font-size: {font_size}px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="text">{text}</div>
            </div>
            <p>ถ้าเห็นข้อความภาษาไทยด้านบน แสดงว่าระบบทำงานปกติ</p>
        </body>
        </html>
        """
        
        return send_file(
            BytesIO(html.encode('utf-8')),
            mimetype='text/html',
            as_attachment=False,
            download_name='preview.html'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/screenshot-url', methods=['POST'])
def screenshot_url():
    """สร้าง URL สำหรับ screenshot service"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF').replace('#', '')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # สร้าง HTML URL
        html_template = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700" rel="stylesheet">
            <style>
                body {{ margin: 0; padding: 0; }}
                .container {{
                    width: 800px;
                    height: 600px;
                    position: relative;
                    background: url('{img_url}') center/cover no-repeat;
                }}
                .text {{
                    position: absolute;
                    left: {x}px;
                    top: {y}px;
                    color: #{color};
                    font-size: {font_size}px;
                    font-family: 'Noto Sans Thai', sans-serif;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="text">{text}</div>
            </div>
        </body>
        </html>
        """
        
        # Encode HTML
        html_base64 = base64.b64encode(html_template.encode('utf-8')).decode('utf-8')
        
        # Screenshot API URLs
        screenshot_urls = {
            # 1. ScreenshotAPI.net (ฟรี 100 ครั้ง/เดือน)
            "screenshotapi": f"https://shot.screenshotapi.net/screenshot?url=data:text/html;base64,{html_base64}&width=800&height=600&output=image&file_type=png",
            
            # 2. Microlink API (ฟรี)
            "microlink": f"https://api.microlink.io/?url=data:text/html;base64,{html_base64}&screenshot=true&meta=false&embed=screenshot.url",
            
            # 3. Page2Images (ฟรี)
            "page2images": f"https://api.page2images.com/directlink?p2i_url=data:text/html;base64,{html_base64}&p2i_size=800x600&p2i_screen=1024x768&p2i_imageformat=png"
        }
        
        return jsonify({
            "success": True,
            "screenshot_urls": screenshot_urls,
            "html_base64": html_base64,
            "usage": "Use any of these URLs to get PNG image"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-html', methods=['POST'])
def get_html():
    """สร้าง HTML สำหรับ HTML to Image node ใน n8n"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        align = data.get('align', 'left')
        valign = data.get('valign', 'top')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # แปลง alignment
        text_align = align
        vertical_align = valign
        
        # สร้าง HTML ที่สมบูรณ์
        # จัดการข้อความหลายบรรทัด
        lines = text.split('\n') if '\n' in text else [text]
        text_html = ''
        for i, line in enumerate(lines):
            line_y = y + (i * int(font_size * 1.2))
            text_html += f'<div class="text-line" style="position: absolute; left: {x}px; top: {line_y}px;">{line}</div>'
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=800">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            width: 800px;
            height: 600px;
            font-family: 'Noto Sans Thai', sans-serif;
            overflow: hidden;
        }}
        .container {{
            width: 800px;
            height: 600px;
            position: relative;
            background-image: url('{img_url}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .text-line {{
            color: {color};
            font-size: {font_size}px;
            font-weight: 400;
            text-align: {text_align};
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
    </style>
</head>
<body>
    <div class="container">
        {text_html}
    </div>
</body>
</html>'''
        
        return jsonify({
            "success": True,
            "html": html,
            "note": "Use this HTML in n8n HTML to Image node"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-html-raw', methods=['POST'])
def get_html_raw():
    """ส่ง HTML โดยตรง (ไม่ใช่ JSON)"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF')
        
        if not img_url:
            return "Error: img_url is required", 400
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            width: 800px;
            height: 600px;
            font-family: 'Noto Sans Thai', sans-serif;
        }}
        .container {{
            width: 800px;
            height: 600px;
            position: relative;
            background: url('{img_url}') center/cover no-repeat;
        }}
        .text {{
            position: absolute;
            left: {x}px;
            top: {y}px;
            color: {color};
            font-size: {font_size}px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="text">{text}</div>
    </div>
</body>
</html>'''
        
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/render-image', methods=['POST'])
def render_image():
    """สร้างรูปภาพ PNG โดยใช้ external service"""
    try:
        data = request.get_json()
        
        img_url = data.get('img_url')
        text = data.get('text', 'Hello')
        x = int(data.get('x', 100))
        y = int(data.get('y', 100))
        font_size = int(data.get('font_size', 48))
        color = data.get('font_color', '#FFFFFF').replace('#', '')
        
        if not img_url:
            return jsonify({"error": "img_url is required"}), 400
        
        # สร้าง HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            width: 800px;
            height: 600px;
            font-family: 'Noto Sans Thai', sans-serif;
        }}
        .container {{
            width: 800px;
            height: 600px;
            position: relative;
            background: url('{img_url}') center/cover no-repeat;
        }}
        .text {{
            position: absolute;
            left: {x}px;
            top: {y}px;
            color: #{color};
            font-size: {font_size}px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="text">{text}</div>
    </div>
</body>
</html>'''
        
        # ใช้ hcti.io (HTML/CSS to Image API)
        # สมัครฟรีได้ที่ https://htmlcsstoimage.com
        hcti_api = "https://hcti.io/v1/image"
        
        # หรือใช้ screenshotapi.net
        html_base64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
        screenshot_url = f"https://shot.screenshotapi.net/screenshot?url=data:text/html;base64,{html_base64}&width=800&height=600&output=image&file_type=png"
        
        # ดึงรูปจาก screenshot service
        response = requests.get(screenshot_url, timeout=30)
        
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('image'):
            return send_file(
                BytesIO(response.content),
                mimetype='image/png',
                as_attachment=True,
                download_name='result.png'
            )
        else:
            # Fallback to SVG
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&amp;display=swap');
      .thai-text {{
        font-family: 'Noto Sans Thai', sans-serif;
        font-size: {font_size}px;
        fill: #{color};
      }}
    </style>
  </defs>
  <image href="{img_url}" width="800" height="600" preserveAspectRatio="xMidYMid slice"/>
  <text x="{x}" y="{y}" class="thai-text">{text}</text>
</svg>'''
            
            return send_file(
                BytesIO(svg_content.encode('utf-8')),
                mimetype='image/svg+xml',
                as_attachment=True,
                download_name='result.svg'
            )
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500