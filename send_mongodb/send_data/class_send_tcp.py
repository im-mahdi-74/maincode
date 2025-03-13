import time
import datetime
from data import Data_pross
import socket

class MarketDataSender:
    def __init__(self, symbol, port, host, login, pas, server, path): 
        self.symbol = symbol
        self.port = port
        self.host = host
        self.login = login
        self.pas = pas
        self.server = server
        self.path = path
        self.trade = None

    def is_working_hours(self):
        current_time = datetime.datetime.now().time()
        start_time = datetime.time(9, 0)  # 9 صبح
        end_time = datetime.time(23, 0)   # 11 شب
        return start_time <= current_time <= end_time

    def test_connection(self):
        try:
            print(f"test conected {self.host}:{self.port}")
            with socket.socket() as test_socket:
                test_socket.settimeout(5)
                test_socket.connect((self.host, self.port))
                print("Done conected one " )
                return True
        except Exception as e:
            print(f"eror to concted one {e}")
            return False

    def send_json_data(self, df):
        json_data = df.to_json(orient='records', force_ascii=False)
        
        try:
            print(f"try to conected ... {self.host}:{self.port}")
            with socket.socket() as client_socket:
                client_socket.settimeout(60)  # افزایش timeout به 60 ثانیه
                print("concting ...")
                client_socket.connect((self.host, self.port))
                print("Done conencted ")
                
                size = str(len(json_data)).ljust(10)
                print(f"sending size data {size}")
                client_socket.send(size.encode())
                
                print("Done send..")
                client_socket.send(json_data.encode())
                
                print("wating server ..")
                response = client_socket.recv(1024).decode()
                print(f'Done {self.symbol} , time : {datetime.datetime.now()}')
                print(f"Server response: {response}")
                
        except socket.timeout:
            print(f"erorr timeout {self.host}:{self.port}")
            raise
        except ConnectionRefusedError:
            print(f"not conected {self.host}:{self.port} ")
            raise
        except Exception as e:
            print(f"Error in sending data: {e}")
            raise

    def run(self):
        self.trade = Data_pross(login=self.login, pas=self.pas, 
                              server=self.server, path=self.path)
        self.trade.init()
        
        # تست اتصال اولیه
        if not self.test_connection():
            print("erorr to contected ones")
        
        while True:
            current_time = datetime.datetime.now()

            if not self.is_working_hours():
                print(f"{self.symbol}: Note time Work ")
                time.sleep(60)
                continue

            if (current_time.minute + 1) % 5 == 0 and current_time.second >= 55:
                try:
                    df = self.trade.df_pross(self.symbol)
                    if not df.empty:
                        try:
                            self.send_json_data(df)
                        except Exception as e:
                            print(f"{self.symbol}: eoro to send data {e}")
                            print("wating to next conected ..")
                        finally:
                            time.sleep(10)
                    else:
                        print(f"{self.symbol}: empity DataFrame")
                        time.sleep(0.1)
                except Exception as e:
                    print(f"{self.symbol}: eror to run {e}")
                    time.sleep(1)
            else:
                time.sleep(0.5) 