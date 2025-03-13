from send_data.class_send_tcp import MarketDataSender

if __name__ == "__main__" : 
    sender = MarketDataSender(
        symbol= 'GBPUSD' , 
        port =  5000 , 
        host ='82.115.20.118', 
        login=225762,
        pas='z$Fh{}3z', 
        server='PropridgeCapitalMarkets-Server',
        path=r"C:\Program Files\Propridge Capital Markets MT5 Terminal\terminal64.exe" , 
        
    )
    sender.run()