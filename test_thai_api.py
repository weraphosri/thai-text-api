import requests
import os
from datetime import datetime

# API Base URL
API_BASE = "https://thai-text-api-production.up.railway.app"

def test_pure_svg():
    """ทดสอบ SVG ภาษาไทย"""
    print("🧪 Testing Pure SVG...")
    
    test_texts = [
        "ทั้งที่ยังรัก",
        "ที่นี่ ยิ้ม สิ้นสุด", 
        "สวัสดีครับ ทดสอบ API",
        "ภาษาไทย Unicode ✅"
    ]
    
    for i, text in enumerate(test_texts, 1):
        url = f"{API_BASE}/pure-svg"
        params = {"text": text}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                filename = f"thai_test_{i}.svg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ SVG {i}: {filename} - {text}")
            else:
                print(f"❌ SVG {i}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ SVG {i}: Exception - {e}")

def test_html_canvas():
    """ทดสอบ HTML Canvas"""
    print("\n🧪 Testing HTML Canvas...")
    
    test_texts = [
        "ทดสอบ HTML Canvas",
        "ภาษาไทย + English Mixed",
        "123 ตัวเลข ภาษาไทย ABC"
    ]
    
    for i, text in enumerate(test_texts, 1):
        url = f"{API_BASE}/html-canvas"
        params = {"text": text}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                filename = f"thai_html_{i}.html"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ HTML {i}: {filename} - {text}")
            else:
                print(f"❌ HTML {i}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ HTML {i}: Exception - {e}")

def test_text_on_image():
    """ทดสอบใส่ข้อความบนรูป"""
    print("\n🧪 Testing Text on Image...")
    
    test_cases = [
        {
            "img_url": "https://picsum.photos/800/600",
            "text": "ทดสอบใส่ข้อความ",
            "x": 100,
            "y": 100,
            "font_size": 48,
            "font_color": "#FFFFFF"
        },
        {
            "img_url": "https://picsum.photos/800/600?random=2",
            "text": "สวัสดีครับ\nบรรทัดที่ 2",
            "x": 50,
            "y": 200,
            "font_size": 36,
            "font_color": "#FFFF00"
        },
        {
            "img_url": "https://picsum.photos/800/600?random=3",
            "text": "ภาษาไทย Unicode ✅",
            "x": 200,
            "y": 300,
            "font_size": 42,
            "font_color": "#FF5722"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        url = f"{API_BASE}/text-on-image"
        
        try:
            response = requests.post(url, json=case, timeout=15)
            
            if response.status_code == 200:
                filename = f"text_on_image_{i}.svg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Text on Image {i}: {filename}")
            else:
                print(f"❌ Text on Image {i}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Text on Image {i}: Exception - {e}")

def test_api_status():
    """ทดสอบสถานะ API"""
    print("\n🧪 Testing API Status...")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Status:", data.get("status"))
            print("📝 Info:", data.get("info"))
        else:
            print(f"❌ API Status: Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ API Status: Exception - {e}")

def test_basic_svg():
    """ทดสอบ SVG พื้นฐาน"""
    print("\n🧪 Testing Basic SVG...")
    
    url = f"{API_BASE}/test"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            filename = "basic_test.svg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Basic SVG: {filename}")
        else:
            print(f"❌ Basic SVG: Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Basic SVG: Exception - {e}")

def run_all_tests():
    """รันทดสอบทั้งหมด"""
    print("🚀 Starting Thai API Tests...")
    print("=" * 50)
    
    # สร้างโฟลเดอร์ผลลัพธ์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = f"thai_api_test_{timestamp}"
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)
    
    # รันทดสอบทั้งหมด
    test_api_status()
    test_basic_svg()
    test_pure_svg()
    test_html_canvas()
    test_text_on_image()
    
    print("\n" + "=" * 50)
    print(f"✅ All tests completed! Check files in: {test_dir}")
    print("📁 Files created:")
    
    # แสดงไฟล์ที่สร้าง
    files = os.listdir('.')
    for file in sorted(files):
        print(f"   • {file}")
    
    print("\n💡 How to view results:")
    print("   • SVG files: Open in browser or image viewer")
    print("   • HTML files: Open in browser")
    print("   • All files support Thai text perfectly!")

if __name__ == "__main__":
    run_all_tests()