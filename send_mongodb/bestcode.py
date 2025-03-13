import time
import datetime
import logging
from pymongo import MongoClient
from data import Data_pross
import os
import certifi
from dotenv import load_dotenv
import schedule

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات اولیه از متغیرهای محیطی
LOGIN = int(os.getenv("MT5_LOGIN", "225762"))
PASSWORD = os.getenv("MT5_PASSWORD", "z$Fh{}3z")
SERVER = os.getenv("MT5_SERVER", "PropridgeCapitalMarkets-Server")
PATH = os.getenv("MT5_PATH", r"C:\Program Files\Propridge Capital Markets MT5 Terminal\terminal64.exe")
SYMBOL = os.getenv("TRADING_SYMBOL", "GBPUSD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mahdi:Mahdi1400@bot.zdhv2.mongodb.net/")

os.environ['SSL_CERT_FILE'] = certifi.where()

# کلاس برای مدیریت اتصال MongoDB
class MongoDBManager:
    def __init__(self, uri, db_name, collection_name):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.last_connection_check = 0
        self.connection_check_interval = 3600  # چک کردن اتصال هر یک ساعت
    
    def connect(self):
        """ایجاد اتصال به MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # تست اتصال
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.last_connection_check = time.time()
            logger.info("اتصال به MongoDB با موفقیت برقرار شد")
            return True
        except Exception as e:
            logger.error(f"خطا در اتصال به MongoDB: {e}")
            self.client = None
            return False
    
    def disconnect(self):
        """بستن اتصال MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("اتصال MongoDB بسته شد")
    
    def ensure_connection(self):
        """اطمینان از وجود اتصال فعال"""
        current_time = time.time()
        
        # اگر اتصال وجود ندارد یا زمان بررسی مجدد فرا رسیده
        if (not self.client or 
            current_time - self.last_connection_check > self.connection_check_interval):
            
            # اگر اتصال قبلی وجود دارد، سلامت آن را بررسی کنیم
            if self.client:
                try:
                    # تست سلامت اتصال فعلی
                    self.client.admin.command('ping', serverSelectionTimeoutMS=2000)
                    # اتصال سالم است، فقط زمان آخرین بررسی را به‌روز کنیم
                    self.last_connection_check = current_time
                    return True
                except Exception:
                    # اتصال مشکل دارد، آن را ببندیم
                    logger.info("اتصال MongoDB قدیمی است یا ناسالم، مجدداً متصل می‌شویم")
                    self.disconnect()
            
            # ایجاد اتصال جدید
            return self.connect()
        
        return True
    
    def update_data(self, df):
        """بروزرسانی داده‌ها با استفاده از تراکنش"""
        if df.empty:
            logger.warning("دیتافریم خالی است!")
            return False
            
        try:
            # اطمینان از اتصال فعال
            if not self.ensure_connection():
                return False
                
            # استفاده از تراکنش برای عملیات بروزرسانی
            with self.client.start_session() as session:
                with session.start_transaction():
                    # حذف داده‌های قدیمی
                    self.collection.delete_many({}, session=session)
                    # درج داده‌های جدید
                    self.collection.insert_many(df.to_dict("records"), session=session)
            
            logger.info("داده‌ها با موفقیت بروزرسانی شدند")
            return True
        except Exception as e:
            logger.error(f"خطا در بروزرسانی داده‌ها: {e}")
            # در صورت خطا در اتصال، آن را بازنشانی می‌کنیم
            if "not connected" in str(e).lower() or "connection" in str(e).lower():
                self.client = None
            return False

# کلاس برای مدیریت داده‌های ترید
class TradingDataManager:
    def __init__(self, login, password, server, path, symbol):
        self.symbol = symbol
        self.trade = None
        self.login = login
        self.password = password
        self.server = server
        self.path = path
        self.last_check = 0
        self.check_interval = 3600  # چک کردن اتصال هر یک ساعت
        
    def initialize(self):
        """آماده‌سازی اتصال به پلتفرم معاملاتی"""
        try:
            self.trade = Data_pross(login=self.login, pas=self.password, server=self.server, path=self.path)
            result = self.trade.init()
            if result:
                logger.info(f"اتصال به پلتفرم معاملاتی برای {self.symbol} برقرار شد")
                self.last_check = time.time()
            else:
                logger.error("اتصال به پلتفرم معاملاتی ناموفق بود")
                self.trade = None
            return result
        except Exception as e:
            logger.error(f"خطا در اتصال به پلتفرم معاملاتی: {e}")
            self.trade = None
            return False
    
    def ensure_connection(self):
        """اطمینان از وجود اتصال فعال"""
        current_time = time.time()
        
        # اگر اتصال وجود ندارد یا زمان بررسی مجدد فرا رسیده
        if (not self.trade or 
            current_time - self.last_check > self.check_interval):
            return self.initialize()
        
        return True
    
    def get_data(self):
        """دریافت داده‌ها از پلتفرم معاملاتی"""
        try:
            if not self.ensure_connection():
                return None
                
            df = self.trade.df_pross(self.symbol)
            return df
        except Exception as e:
            logger.error(f"خطا در دریافت داده‌ها: {e}")
            # در صورت خطا، اتصال را بازنشانی می‌کنیم
            self.trade = None
            return None

# تابع اصلی برنامه
def main():
    """تابع اصلی برنامه"""
    logger.info("شروع برنامه")
    
    # ایجاد مدیریت‌کننده‌های داده و اتصال (یکبار در ابتدای برنامه)
    mongo_manager = MongoDBManager(MONGO_URI, "bot", f"{SYMBOL}_collection")
    trading_manager = TradingDataManager(LOGIN, PASSWORD, SERVER, PATH, SYMBOL)
    
    # اتصال اولیه
    if not mongo_manager.connect():
        logger.error("اتصال اولیه به MongoDB ناموفق بود")
        return
        
    if not trading_manager.initialize():
        logger.error("اتصال اولیه به پلتفرم معاملاتی ناموفق بود")
        return
    
    # تعریف تابع اجرا برای هر بار به‌روزرسانی
    def update_job():
        logger.info(f"شروع به‌روزرسانی داده‌ها برای {SYMBOL} در {datetime.datetime.now()}")
        try:
            df = trading_manager.get_data()
            if df is not None and not df.empty:
                if mongo_manager.update_data(df):
                    logger.info(f"به‌روزرسانی داده‌ها برای {SYMBOL} با موفقیت انجام شد")
                else:
                    logger.error(f"به‌روزرسانی داده‌ها برای {SYMBOL} ناموفق بود")
            else:
                logger.warning(f"داده‌ای برای {SYMBOL} دریافت نشد")
        except Exception as e:
            logger.error(f"خطای اصلی در به‌روزرسانی: {e}")
    
    # تنظیم زمان‌بندی برای اجرای هر 5 دقیقه
    schedule.every(5).minutes.do(update_job)
    logger.info("زمان‌بندی تنظیم شد: اجرا هر 5 دقیقه")
    
    # اجرای اولیه
    update_job()
    
    # حلقه اصلی برنامه
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در حلقه اصلی: {e}")
    finally:
        # در پایان برنامه اتصال را می‌بندیم
        mongo_manager.disconnect()
        logger.info("برنامه پایان یافت")

if __name__ == "__main__":
    main()