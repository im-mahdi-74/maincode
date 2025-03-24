import requests



# توکن ربات خود را وارد کنید
bot_token = '8076261587:AAEVUGzE9qIJGbozwV_BqAnnXWFpUyZwIGs'
# شناسه کانال خود را وارد کنید (شناسه کانال با علامت @ شروع می‌شود)
channel_id = '@QuantityOption'


def send_message(bot_token, channel_id, message):


    # ساخت URL برای ارسال پیام
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    # پارامترهای درخواست
    params = {
        'chat_id': channel_id,
        'text': message
    }

    # ارسال درخواست POST
    response = requests.post(url, params=params)

    # بررسی موفقیت‌آمیز بودن ارسال پیام
    if response.status_code == 200:
        print('پیام با موفقیت ارسال شد.')
    else:
        print(f'خطا در ارسال پیام: {response.status_code}')


from datetime import datetime, timedelta, time as datetime_time, timezone
import time
import os
import certifi
import json
from pymongo import MongoClient


os.environ['SSL_CERT_FILE'] = certifi.where()

def is_working_hours():
    current_time = datetime.now().time()
    start_time = datetime_time(10, 0)  # 9 صبح
    end_time = datetime_time(22, 0)   # 10 شب
    return start_time <= current_time <= end_time

# اتصال به MongoDB با مدیریت خطا
def get_mongo_connection():
    connection_string = "mongodb+srv://mahdi:Mahdi1400@bot.zdhv2.mongodb.net/"
    try:
        client = MongoClient(connection_string)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"خطا در اتصال به MongoDB: {e}")
        return None

def read_recent_orders():
    try:
        client = get_mongo_connection()
        if not client:
            return None
        
        db = client["order"]
        collection = db["orders"]
        
        # محاسبه timestamp یک دقیقه قبل
        current_timestamp = time.time()
        one_minute_ago_timestamp = current_timestamp - 60  # 60 ثانیه قبل
        
        # پیدا کردن اسناد یک دقیقه اخیر با استفاده از timestamp
        query = {"timestamp": {"$gte": one_minute_ago_timestamp}}
        recent_orders = list(collection.find(query, {"_id": 0}))
        
        print(f"Checking orders after timestamp: {one_minute_ago_timestamp  }")
        print(f"Current timestamp: {current_timestamp,datetime.now()}")
        print(f"Found {len(recent_orders)} orders")
        
        return recent_orders
    except Exception as e:
        print(f"error in reading orders : {e}")
        return None
    finally:
        if client:
            client.close()


def times():

    now = datetime.now()
    current_minute = now.minute
    current_second = now.second + now.microsecond / 1_000_000  # محاسبه ثانیه با اعشار

    if (current_minute + 1) % 5 == 0 and current_second >= 59:
        return True
    else:
        return False

def make_message(recent_data):
    massage = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    for item in recent_data:
        for key, value in item.items():
            if key != "timestamp" and isinstance(value, (int, float)):
                massage.append(f"{key} -> Buy : {value:.2f} , Sell : {1-value:.2f}")
    return "\n".join(massage)


# اجرای برنامه
if __name__ == "__main__":
    while True:
        time.sleep(0.1)
        if not is_working_hours():
            print("خارج از ساعت کاری (9 صبح تا 10 شب)")
            time.sleep(60)  # یک دقیقه صبر می‌کنیم
            continue
        #if (datetime.now().minute + 1) % 5 == 0 and(datetime.now().second +  datetime.now().microsecond / 1_000_000) >= 58.6:
        if times():
            recent_data = read_recent_orders()
            message = make_message(recent_data)
            print(message)
            if recent_data:
                send_message(bot_token, channel_id, message)
                time.sleep(240)








    
