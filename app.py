import os
import requests
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, features
from io import BytesIO

app = Flask(__name__)

def download_thai_font():
    """ดาวน์โหลดฟอนต์ไทยถ้าไม่มี"""
    font_dir = "/tmp/fonts"
    font_path = os.path.join(font_dir, "NotoSansThai-Regular.ttf")
    
    # สร้างโฟลเดอร์ถ้าไม่มี
    os.makedirs(font_dir, exist_ok=True)
    
    if not os.path.exists(font_path):
        try:
            # ดาวน์โหลดฟอนต์จาก Google Fonts
            font_url = "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai-Regular.ttf"
            
            print("Downloading Thai font...")
            response = requests.get(font_url, timeout=30)
            response.raise_for_status()
            
            with open(font_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Font downloaded: {font_path}")
            return font_path
            
        except Exception as e:
            print(f"Failed to download font: {e}")
            return None
    
    return font_path

def get_font(size=48):
    """หาฟอนต์ไทยที่ดีที่สุด"""
    # ลองดาวน์โหลดฟอนต์ไทยก่อน
    downloaded_font = download_thai_font()
    if downloaded_font and os.path.exists(downloaded_font):
        try:
            return ImageFont.truetype(downloaded_font, size)
        except Exception as e:
            print(f"Failed to load downloaded font: {e}")
    
    # ลองหาฟอนต์ในระบบ
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda.ttf',
        '/usr/share/fonts/truetype/thai-tlwg/Garuda-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Failed to load {font_path}: {e}")
                continue
    
    # ใช้ default font
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def check_raqm_support():
    """ตรวจสอบว่า PIL มี RAQM support หรือไม่"""
    try:
        return features.check_feature('raqm')
    except:
        return False

@app.route('/')
def home():
    raqm_status = "✅ RAQM supported" if check_raqm_support() else "❌ RAQM not supported"
    
    # ตรวจสอบฟอนต์
    font_status = "❌ No Thai font"
    try:
        test_font = get_font(20)
        if test_font:
            font_status = "✅ Thai font loaded"
    except:
        pass
    
    return jsonify({
        "status": "Thai Text API ✅",
        "raqm_support": raqm_status,
        "font_support": font_status,
        "info": "Auto-downloading Thai fonts if needed"
    })

@app.route('/test')
def test():
    """ทดสอบ Thai text shaping"""
    img = Image.new('RGB', (800, 400), '#1976D2')
    draw = ImageDraw.Draw(img)
    
    # ข้อความทดสอบ
    test_text = "ทั้งที่ยังรัก\nที่นี่ ยิ้ม สิ้นสุด\nสวัสดีครับ"
    
    try:
        font = get_font(36)
        status_font = get_font(18)
        
        # ตรวจสอบ RAQM และฟอนต์
        has_raqm = check_raqm_support()
        
        lines = test_text.split('\n')
        y_pos = 50
        
        for line in lines:
            if has_raqm:
                # ใช้ RAQM
                draw.text(
                    (50, y_pos), 
                    line, 
                    font=font, 
                    fill='white',
                    language='th',
                    direction='ltr'
                )
            else:
                # ไม่มี RAQM
                draw.text((50, y_pos), line, font=font, fill='white')
            y_pos += 60
        
        # แสดงสถานะ
        if has_raqm:
            draw.text((50, 320), "✅ RAQM + Thai Font: Perfect!", 
                     font=status_font, fill='#4CAF50')
        else:
            draw.text((50, 320), "⚠️  Basic rendering (may have sara loy issues)", 
                     font=status_font, fill='#FF9800')
        
    except Exception as e:
        # ถ้า error ให้แสดงข้อความ error
        error_font = ImageFont.load_default()
        draw.text((50, 100), f"Font Error: {str(e)}", font=error_font, fill='white')
        draw.text((50, 150), "Downloading fonts...", font=error_font, fill='yellow')
    
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=90)
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
        language = data.get('language', 'th')
        
        if not img_url:
            return jsonify({"error": "ต้องมี img_url"}), 400
        
        # โหลดรูป
        response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # หาฟอนต์
        font = get_font(font_size)
        
        # เพิ่มข้อความ
        lines = text.split('\n')
        has_raqm = check_raqm_support()
        
        for i, line in enumerate(lines):
            if has_raqm:
                # ใช้ RAQM สำหรับ proper text shaping
                draw.text(
                    (x, y + i * (font_size + 5)), 
                    line, 
                    font=font, 
                    fill=color,
                    language=language,
                    direction='ltr'
                )
            else:
                # fallback สำหรับ non-RAQM
                draw.text((x, y + i * (font_size + 5)), line, font=font, fill=color)
        
        # ส่งรูปกลับ
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)