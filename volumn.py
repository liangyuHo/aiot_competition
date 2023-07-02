import numpy as np
import time
import datetime
import os
import csv
import serial
import requests

# 回傳volumn data
class Volumn_detect:
    def __init__(self):
        self.volumn = None
        current_minute = datetime.datetime.now().minute
        
    def set_volumn_value(self, value):
        self.volumn = value
    
    # 及時回傳分貝值
    def get_volumn_value(self):
        return self.volumn
    
    # 每分鐘寫到一個新的csv檔
    def write_volumn_to_csv(self):
        self.csv_writer.write_value(self.volumn)    
    
    # 初始化
    def start_csv_writing(self):
        self.csv_writer = CSVWriter('DB_data\per_minute_volumn_data')

class CSVWriter:
    def __init__(self, file_prefix):
        self.file_prefix = file_prefix
        # 設定csv路徑
        self.file_path = self.generate_file_path()
        self.current_minute = datetime.datetime.now().minute
        self.file = None
        self.writer = None

    def generate_file_path(self):
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        self.file_name = self.file_prefix + '_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + '.csv'
        self.file_path = os.path.join(self.file_path, self.file_name)
        return self.file_path


    def write_value(self, value):
        if self.current_minute != self.get_current_minute():
            self.close_file()
            self.generate_file_path()
            self.current_minute = datetime.datetime.now().minute
        self.file = open(self.file_path, mode='a', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),value])

    def close_file(self):
        if self.file:
            self.file.close()

    def get_current_minute(self):
        current_minute = datetime.datetime.now().minute
        return current_minute
        
if __name__ == "__main__":
    volumn_detect = Volumn_detect()
    volumn_detect.start_csv_writing()
    ser = serial.Serial()
    ser.port = "COM6"
    ser.baudrate = 115200
    ser.timeout = 0.5          #non-block read 0.5s
    ser.writeTimeout = 0.5     #timeout for write 0.5s
    ser.xonxoff = False    #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
    try: 
        ser.open()
    except Exception as ex:
        print ("open serial port error " + str(ex))
        exit()
    
    if ser.isOpen():   
        try:
            ser.flushInput() #flush input buffer
            ser.flushOutput() #flush output buffer
            while(1):
                response = ser.readline()
                response = response.decode('utf-8').strip()
                volumn_detect.set_volumn_value(response)
                print(volumn_detect.get_volumn_value())

                # 用 post 傳資料
                DB_data = {"DB": response}
                response = requests.post("http://localhost:8000/DBdata/", json=DB_data)  

                volumn_detect.write_volumn_to_csv()
                # 設定幾秒讀一次，沒設的話他會一秒太多筆   
                time.sleep(0.5)
            ser.close()
        except Exception as e1:
            print ("communicating error " + str(e1))
    
    else:
        print ("open serial port error")