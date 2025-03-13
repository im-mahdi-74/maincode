import time
import datetime
from pymongo import MongoClient
from data import Data_pross
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

# تنظیمات اولیه
login = 225762
pas = 'z$Fh{}3z'
server = 'PropridgeCapitalMarkets-Server'
path = r"C:\Program Files\Propridge Capital Markets MT5 Terminal\terminal64.exe"
symbol = "EURUSD"

# اتصال به MongoDB با مدیریت خطا
def get_mongo_connection():
    connection_string = "mongodb+srv://mahdi:Mahdi1400@bot.zdhv2.mongodb.net/"
    client = MongoClient(connection_string)
    try:
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"خطا در اتصال به MongoDB: {e}")
        return None

client = get_mongo_connection()
if not client:
    exit("Not Conected MongoDB")

db = client["bot"]
collection = db[f"{symbol}_collection"]

# تابع بهروزرسانی دادهها با مدیریت خطا
def update_collection(df_new):
    try:
        # جایگزینی تمام دادهها با استفاده از تراکنش
        with client.start_session() as session:
            with session.start_transaction():
                # حذف دادههای قدیمی
                collection.delete_many({}, session=session)
                # درج دادههای جدید
                collection.insert_many(df_new.to_dict("records"), session=session)
        print("دادهها با موفقیت بهروزرسانی شدند!")
    except Exception as e:
        print(f"خطا در بهروزرسانی دادهها: {e}")

# تابع اصلی با زمانبندی دقیق
def run(symbol):
    trade = Data_pross(login=login, pas=pas, server=server, path=path)
    trade.init()
    
    while True:
        current_time = datetime.datetime.now()
        # اجرا هر ۵ دقیقه در ثانیه ۵۵
        if (datetime.datetime.now().minute + 1) % 5 == 0  and current_time.second >= 55:
            try:
                df = trade.df_pross(symbol)
                if not df.empty:
                    update_collection(df)
                    print(f'Done {symbol} , time : {datetime.datetime.now()}')
                    time.sleep(240)
                else:
                    print("دیتافریم خالی است!")
                # خواب تا شروع دقیقه بعدی
                    time.sleep(0.1)
                    continue
            except Exception as e:
                print(f"خطا در اجرا: {e}")
                time.sleep(1)
        else:
            time.sleep(0.5)

if __name__ == "__main__":
    run(symbol)









