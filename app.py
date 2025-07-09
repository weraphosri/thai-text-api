import os
from flask import Flask, request, send_file, jsonify, redirect
from io import BytesIO
import requests
import urllib.parse
import json

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Thai Text API ✅",
        "info": "Simple working solution for Thai text on images",
        "endpoints": {
            "/text-on-image": "POST - Add Thai text to image",
            "/test": "GET - Test Thai rendering",
            "/simple": "GET - Simple text image"
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
    """เพิ่มข้อความบนรูป"""
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
        
        # วิธีที่ 1: ใช้ Statically.io (Free CDN with image manipulation)
        # รองรับ text overlay แต่ภาษาไทยอาจมีปัญหา
        statically_url = f"https://cdn.statically.io/img/{img_url.replace('https://', '').replace('http://', '')}/w=800,h=600"
        
        # วิธีที่ 2: สร้าง HTML และแปลงเป็นรูป
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    width: 800px;
                    height: 600px;
                    position: relative;
                    overflow: hidden;
                }}
                .container {{
                    width: 100%;
                    height: 100%;
                    position: relative;
                    background-image: url('{img_url}');
                    background-size: cover;
                    background-position: center;
                }}
                .text {{
                    position: absolute;
                    left: {x}px;
                    top: {y}px;
                    color: {color};
                    font-size: {font_size}px;
                    font-family: 'Noto Sans Thai', sans-serif;
                    text-align: {align};
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
        
        # วิธีที่ 3: ใช้ API ที่ทำงานได้แน่นอน - กลับไปใช้ SVG
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
        
        # ส่ง SVG กลับไป (ทำงานได้แน่นอน)
        return send_file(
            BytesIO(svg_content.encode('utf-8')),
            mimetype='image/svg+xml',
            as_attachment=True,
            download_name='result.svg'
        )
        
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)