from fastapi import FastAPI, UploadFile, File
import pyautogui
import time
import pandas as pd
import os
import csv
from fastapi.responses import HTMLResponse
import shutil
from pathlib import Path
from mp3_2_txt import convert
from summarize import summary
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

## 添加 cors ，讓 header 是 allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def read_root():
    return {}



##############################################################################
##### 上傳 mp3 轉成 txt 並回傳大綱
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    print(file.filename)
    with Path(f"uploads/{file.filename}").open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    txtFile = convert(file.filename)
    summary(txtFile)
    return {"filename": file.filename}




##############################################################################
##### 貼文(新增、刪除、修改、查詢)
class Post(BaseModel):
    user: str
    text: str

@app.post("/post/")
async def create_post(post : Post):
    file_exists = Path('posts.csv').is_file()
    with open('posts.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['user', 'text'])
        writer.writerow([post.user, post.text])
    return {"message": "Post created"}

@app.post("/delete/")
async def delete_post(id: int):
    all_post = pd.read_csv('posts.csv')
    all_post = all_post.drop(index=id)
    all_post.to_csv('posts.csv',index=False)

@app.post("/modify/")
async def delete_post(id: int, context: str):
    all_post = pd.read_csv('posts.csv')
    all_post.loc[id, 'text'] = context
    all_post.to_csv('posts.csv',index=False)

@app.get("/search_post")
def get_post():
    all_post = pd.read_csv('posts.csv')
    return {}





##############################################################################
##### 歷史所有會議紀錄
@app.get("/meeting_record")
def get_meeting_record():
    record = []
    for root, dirs, files in os.walk('meeting_text/'):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                record.append(file.read())
    ## record 存著所有會議紀錄
    return {'record':record}



##############################################################################
##### 五分鐘內辦公室人數
class DataItem(BaseModel):
    people: int

@app.post("/peopleData/")    
async def receive_data(item: DataItem):
    # print(item.people)
    global peopleNum
    peopleNum = item.people
    return {}



##############################################################################
##### 分貝數
class DBValue(BaseModel):
    DB: float

@app.post("/DBdata/")
async def get_DB(item: DBValue):
    global DB_data
    DB_data = item.DB
    print(DB_data)
    return {}



##############################################################################
##### 取得五分鐘內的身體資料(手錶數據)，包含心情指數、心跳或血氧等
@app.get("/watch")
def get_watch_data():
    # 獲取當前滑鼠的位置
    current_mouse_position = pyautogui.position()

    # 移動鼠標到指定位置(關閉手環偵測)
    target_position = (100, 100)  
    pyautogui.moveTo(target_position)
    pyautogui.click()

    # 移動鼠標到指定位置(開啟手環偵測)
    target_position = (100, 100)  
    pyautogui.moveTo(target_position)
    pyautogui.click()

    # 打開手錶 CSV 
    df = pd.read_csv('example.csv')

    # 刪除手錶 csv
    if os.path.exists('example.csv'):
        # 删除文件
        os.remove('example.csv')
    # 回傳資料
    return {"data":df}



##############################################################################
##### 五分鐘內環境數據，包含四合一跟CO2的
@app.get("/environment")
def get_environment():
    return {}


##############################################################################
##### 過往辦公室人數
@app.get("/people_past")
def get_people_past():
    return {}



##############################################################################
##### 預測的健康數據，時間可以指定(以小時或天計算)
@app.get("/health_predict")
def get_health_predict():
    return {}


