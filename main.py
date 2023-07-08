from fastapi import FastAPI, UploadFile, File, Form
import pyautogui
import time
import pandas as pd
import os
import csv
import json
import numpy as np
import pickle
from fastapi.responses import HTMLResponse
import shutil
from pathlib import Path
from mp3_2_txt import convert, texts_to_one, reset_dir
from summarize import summary
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from keras.models import save_model, load_model




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
    result = []
    print(all_post.iloc[0][0],all_post.iloc[0][1])
    for i in range(all_post.shape[0]):
        result.append({"user":all_post.iloc[i][0],"context":all_post.iloc[i][1]})
    return result



##############################################################################
##### 辦公室環境狀態
@app.get("/status")
def get_all_status():
    return {"people_now":peopleNum,"people_hour":0,
            "temp":four_environment['temp'],"hpa":four_environment['hpa'],
            "humidity":four_environment['%RH'],"gas":four_environment['ohms'],
            "co2":0, "DB":DB_data}




##############################################################################
##### 歷史所有會議紀錄
@app.get("/meeting_record")
def get_meeting_record():    
    # 打開 json 檔案
    with open('.\meeting_text\meeting.json', 'r') as file:
    # 載入 JSON 檔案
        meeting_content = json.load(file)
    ## record 存著所有會議紀錄
    return meeting_content  



##############################################################################
##### 取得五分鐘內的身體資料(手錶數據)，包含心情指數、心跳或血氧等
@app.get("/watch")
def get_watch_data():
    return {"HR":health_current[0], "SPO2":health_current[1], 
            "activity":health_current[2], "mood":health_current[3]}




##############################################################################
##### 取得五分鐘內的身體資料(手錶數據)，包含心情指數、心跳或血氧等
@app.get("/watch_predict")
def predict_health():
    return{"HR_pre":health_predict[0][0], "RR_pre":health_predict[0][0], 
            "R_pre":health_predict[0][0], "SPO2_pre":health_predict[0][0]}




##############################################################################
##### 預測的健康數據，時間可以指定(以小時或天計算)

feature = None
def load_feature_data():
    global feature
    if feature is None:
        feature = pd.read_csv('./watch/health_data.csv',sep=',',header=None)[:600]

def mood_score(data):
    mood_score = 0    
    # motion flag
    if data['motion'] == 0:
        mood_score += 5
    # HR
    if data['HR'] >= 60 and data['HR'] <= 100:
        mood_score += ((data['HR'] - 60) / 40) * 50
    # SpO2
    if data['SpO2'] >= 90:
        mood_score += ((data['SpO2'] - 90) / 10) * 50
    return mood_score


@app.post("/health_predict/")
async def get_health_predict(health:Dict):
    ## 創 activity
    activity = {0:"Rest",1:"Other",2:"Walk",3:"Run",4:"Bike",5:"Rhythmic"}
    
    global feature    
    ## 一開始抓599筆資料
    load_feature_data()
    ## 處理 feature 讓 feature 保持 600 
    new_rows = pd.DataFrame([health['HR'],health['SpO2'],health['RR'],health['R'],
                                 health['activity'],health['motion'],health['hrconf'],
                                 health['rrconf'],health['wspo2conf']]).T
    feature = pd.concat([feature, new_rows], ignore_index=True)
    if len(feature)>= 600:
        feature = feature.tail(600)
  
    ## 心情指數
    mood = mood_score(health)
  
    ## 抓模型下來，預測結果
    loaded_model = load_model('./watch/model.h5')
    predict = loaded_model.predict(feature[[0,2,3,1]].to_numpy().reshape(-1,600,4)).reshape((-1, 60, 4))
    
    ## 取得當前數據
    global health_current
    health_current = []
    health_current.append(health['HR'])
    health_current.append(health['SpO2'])
    health_current.append(activity[health['activity']])
    health_current.append(mood)

    ## 取得預測結果
    global health_predict
    health_predict = np.mean(predict,axis=1)
    
   




##############################################################################
##### 五分鐘內環境數據，包含四合一跟CO2的

@app.post("/environment/")
def get_environment(four_in_one:Dict):
    global four_environment
    four_environment = four_in_one
    



##############################################################################
##### 分貝數
class DBValue(BaseModel):
    DB: float

@app.post("/DBdata/")
async def get_DB(item: DBValue):
    global DB_data
    DB_data = item.DB




##############################################################################
##### 五分鐘內辦公室人數
class DataItem(BaseModel):
    people: int

@app.post("/peopleData/")    
async def receive_data(item: DataItem):
    # print(item.people)
    global peopleNum
    peopleNum = item.people
    





##############################################################################
##### 上傳 mp3 轉成 txt 並回傳大綱
@app.post("/upload/")
async def upload_file(title: str = Form(...) ,  file: UploadFile = File(...)):
    print(file.filename)
    with Path(f"uploads/{file.filename}").open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    txt_path,meeting_time = convert(file.filename)
    print(os.getcwd())
    meeting_context = texts_to_one(txt_path)
    keyword = summary(meeting_context)
    # meeting_time,meeting_context,keyword
    with open('.\meeting_text\meeting.json','r') as jsfile:
        try:
            data = json.load(jsfile)
        except:
            data = []
            pass
        data.append({"context":meeting_context,"keyword":keyword,"meeting_time":meeting_time})
        
    with open('.\meeting_text\meeting.json','w') as jsfile:
        json.dump(data, jsfile)
    
    reset_dir(txt_path)




