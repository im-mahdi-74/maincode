import socket
import time

def test_port(host, port):
    try:
        print(f"تلاش برای اتصال به {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✅ پورت {port} باز است")
            print(f"زمان پاسخ: {(end_time - start_time):.2f} ثانیه")
        else:
            print(f"❌ پورت {port} بسته است")
            print(f"کد خطا: {result}")
            
    except socket.gaierror:
        print(f"❌ خطا در یافتن هاست {host}")
    except socket.error as e:
        print(f"❌ خطای سوکت: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # تست سرور
    host = "82.115.20.118"  # آدرس IP سرور
    ports = [5000, 5001, 5002 , 5003 , 5004 , 5005 , 5006 , 5007 , 5008 ,5009]  # پورت‌هایی که می‌خواهید تست کنید
    
    for port in ports:
        test_port(host, port)
        print("-" * 50)