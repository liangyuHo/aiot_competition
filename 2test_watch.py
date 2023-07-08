import time
import os
import sys
from tkinter import W
import serial
import csv
import signal
import requests
from arg_parser import parse_arguments

args = parse_arguments()
      
       
if __name__ == "__main__":
    #csv_filename = 'health_watch_data2.csv'
    ser = serial.Serial()
    ser.port = args.COM
    ser.baudrate = 230400
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
            #ser.flushInput() #flush input buffer
            #ser.flushOutput() #flush output buffer
            command = 'set_cfg stream ascii'
            ser.write((command + '\n').encode())
            time.sleep(1)
            command2 = 'read ppg 5'
            ser.write((command2 + '\n').encode())
            time.sleep(1)


            while(1):
                dic = {}
                try:
                    response = ser.readline().decode().strip()
                    data = response.split(',')
                    #response = ser.readline()
                    if len(data) >= 10:
                        # print(data)    
                        dic['HR'] = data[2]
                        dic['SpO2'] = data[9]
                        dic['RR'] = data[4]
                        dic['R'] = data[7]
                        dic['activity'] = data[6]
                        dic['motion'] = data[12]
                        dic['hrconf'] = data[3]
                        dic['rrconf'] = data[5]
                        dic['wspo2conf'] = data[8]
                        print(dic)

                        # with open('./health_data.csv','a',newline = '') as file:
                        #     write = csv.writer(file)
                        #     write.writerow([data[2],data[9],data[4],data[7],data[6],data[12],data[3],data[5],data[8]])
                        try:
                            requests.post('http://'+args.IP+'/health_predict/',json = dic)
                        except:
                            pass
                except KeyboardInterrupt:
                    ser.close()
                time.sleep(0.5)
            ser.close()
       
    
        except:
            print ("open serial port error")
        
        