# aiot_competition
## 資料夾
```
├── DB_data (存放分貝紀錄)
├── meeting_text (存放會議記錄)
├── people_data (存放歷史人數紀錄)
├── ssd_inception_v2_coco_2017_11_17 (辨識人臉)
|   ├── saved_model
├── textrank4zh (計算單辭重要性)
├── uploads (上傳 mp3)
├── txt (暫存 mp3 文字檔)
└── wav (暫存 分割的 wav )
```

## 安裝 ffmpeg
* 到 https://github.com/BtbN/FFmpeg-Builds/releases 下載 ffmpeg-master-latest-win64-gpl.zip
* 解壓縮
* 將 ffmpeg-master-latest-win64-gpl\bin 添加至環境變數

## 安裝python package
```
pip install -r requirements.txt
```

## 執行
* 先確定IP，到終端下輸入
```
ipconfig   
```
** 確定 ipv4 的值

* 開啟 fastapi 
```
uvicorn main:app --host [ip] --port 8000  --reload
```


* 執行 people.py IP (紀錄人數，需要一直執行，透過 POST 傳訊息給 main)
```
python people.py --IP [ip]
```

* 執行 volumn.py IP USB_PORT(偵測分貝數，透過 POST 傳資料給 main)
```
python volumn.py --IP [ip] --COM [COM]
```
* 執行 2test_watch.py (透過 usb 蒐集手錶資訊)
```
python 2test_watch.py --IP [ip] --COM [COM]
```