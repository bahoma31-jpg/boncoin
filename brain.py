import os
import json
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2 import service_account
from PIL import Image, ImageDraw, ImageFont

# --- 1. الإعدادات اللوجستية (تأكد من مطابقتها لجهازك) ---
SPREADSHEET_ID = '1PLCAYBdwDyC75xTf5nsD3YpcLLzCUooyg1Jj11b5-s'
# اسم الورقة كما رأيناه في صورتك [file:84]
RANGE_NAME = "convertcsv (1)!C2:C" # جرب بدون علامات التنصيص المفردة الداخلية [file:88] 
GENAI_API_KEY = "AIzaSyAJNUKt4CbiUCRhkyLzwPhsH2XySPf6auQ"
# ملف الاعتماد والخطوط كما ظهرت في مجلدك [file:87]
SERVICE_ACCOUNT_FILE = 'credentials.json' 
ARABIC_FONT = "Amiri-Bold.ttf"
BACKGROUND_IMG = "background.jpg"

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

def fetch_data():
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"[!] خطأ في جلب البيانات: {e}")
        return []

def analyze_and_draw():
    data = fetch_data()
    if not data:
        print("[-] لا توجد بيانات للمعالجة.")
        return

    os.makedirs('designed_posts', exist_ok=True)
    print(f"[*] تم استطلاع {len(data)} هدفاً. بدء العمليات...")

    for i, row in enumerate(data):
        if not row: continue
        text = row[0]
        
        try:
            print(f"[*] جاري معالجة البيت {i+1}...")
            # إرسال الصورة والنص للتحليل
            img = Image.open(BACKGROUND_IMG)
            prompt = f"أعطني إحداثيات (x,y) ولون Hex وحجم خط لوضع هذا النص على الصورة: {text}. الرد JSON فقط."
            response = model.generate_content([prompt, img])
            style = json.loads(response.text)

            # التنفيذ الفني
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(ARABIC_FONT, style.get('font_size', 50))
            draw.text((style['x'], style['y']), text, fill=style['color'], font=font)
            
            output = f"designed_posts/post_{i+1}.png"
            img.save(output)
            print(f"[+] تم إنجاز المهمة: {output}")
        except Exception as e:
            print(f"[!] فشل في التصميم {i+1}: {e}")

if __name__ == "__main__":
    print("=== بدء تنفيذ النظام الاستراتيجي الشامل ===")
    analyze_and_draw()
    print("=== تمت المهمة، التوفيق من الله وحده ===")
