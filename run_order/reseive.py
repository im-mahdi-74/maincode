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

def save_to_json( acc_buy , acc_sell ):
    # خواندن داده‌های اخیر
    recent_data = read_recent_orders()
    
    try:
        # اگر داده‌ای وجود نداشت یا خطایی رخ داد
        if recent_data is None:
            print("Error in getting orders")
            return False
        
        # اگر داده‌های جدیدی وجود نداشت، فایل را با آرایه خالی بازنویسی کن
        if len(recent_data) == 0:
            with open(r'C:\Users\Administrator\Documents\code\deep-for-binary-pred-forex\trading_signals.json' , 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            print("No new orders found. JSON file cleared.")
            return True
        
        # تبدیل داده‌ها به سیگنال‌های معاملاتی
        signals = []
        for item in recent_data:
            signal_item = {}
            
            # حلقه روی همه کلیدها به جز timestamp
            for key, value in item.items():
                if key != "timestamp" and isinstance(value, (int, float)):

                    # if key == "GBPUSD":
                    #     acc_buy = 0.6
                    #     acc_sell = 0.4
                    # else : 
                    #     acc_buy = 0.7
                    #     acc_sell = 0.3
                    if value > acc_buy:  # بالای 75%
                        signal_item[key] = "BUY"
                    elif value < acc_sell:  # زیر 25%
                        signal_item[key] = "SELL"
                    else:
                        signal_item[key] = "NONE"  # بین 25% تا 75%
            
            signals.append(signal_item)
        print(f'scc : {recent_data} , time : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} , timefile : {time.ctime(recent_data[0]["timestamp"])}')
        combined_dict = {}
        for item in signals:
            combined_dict.update(item)

        # ذخیره سیگنال‌ها در فایل JSON
        with open(r'C:\Users\Administrator\Documents\code\deep-for-binary-pred-forex\trading_signals.json', 'w', encoding='utf-8') as f:
            json.dump(combined_dict, f, ensure_ascii=False, indent=4)
        
        print(f"Saved {len(signals)} trading signals to JSON")
        return True
        
    except Exception as e:
        print(f"Error in saving to JSON: {e}")
        return False

def times():

    now = datetime.now()
    current_minute = now.minute
    current_second = now.second + now.microsecond / 1_000_000  # محاسبه ثانیه با اعشار

    if (current_minute + 1) % 5 == 0 and current_second >= 58.6:
        return True
    else:
        return False

acc_buy = 0.65
acc_sell = 0.35

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
            success = save_to_json(acc_buy,acc_sell)
            if success:
                print("orders saved successfully in trading_signals.json")
                time.sleep(240)

            if not success:
                print("Waiting before next attempt...")








