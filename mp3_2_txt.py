import os
import shutil
import speech_recognition as sr
import concurrent.futures
import wave
import json
import numpy as np
#from google.colab import files
from inlp.convert import chinese
from pydub import AudioSegment
#import ffmpeg
import subprocess
from datetime import datetime

#@markdown 設定錄音檔的分割大小，單位：秒。時間太長，轉文字的效果會較差。
CutTimeDef = 5 #@param {type:"integer"} 
#@markdown 設定 wav 切割檔的暫存目錄
wav_path='wav\\' #@param {type:"string"}
#@markdown 設定文字檔暫存目錄。將特定秒數(CutTimeDef)的音檔轉為文字
txt_path='txt\\' #@param {type:"string"}
#@markdown 執行緖的數量
thread_num = 10 #@param {type:"number"}

# 建立 wav path
if not os.path.exists(wav_path):
  os.mkdir(wav_path)
# 建立 txt path
if not os.path.exists(txt_path):
   os.mkdir(txt_path)

voiceLanguage="zh-TW" #@param {type:"string"}
def reset_dir(path):
    try:
        os.mkdir(path)
    except Exception:
      chk = 'y'
      if chk=="y":
        shutil.rmtree(path)
        os.mkdir(path)
 
def CutFile(WavName, target_path):
 
    # print("CutFile File Name is ", WavName)
    f = wave.open(WavName, "rb")
    params = f.getparams()    
    nchannels, sampwidth, framerate, nframes = params[:4]
    CutFrameNum = framerate * CutTimeDef
    # 讀取格式資訊
    # 一次性返回所有的WAV檔案的格式資訊，它返回的是一個組元(tuple)：聲道數, 量化位數（byte    單位）, 採
    # 樣頻率, 取樣點數, 壓縮型別, 壓縮型別的描述。wave模組只支援非壓縮的資料，因此可以忽略最後兩個資訊
 
    # print("CutFrameNum=%d" % (CutFrameNum))
    # print("nchannels=%d" % (nchannels))
    # print("sampwidth=%d" % (sampwidth))
    # print("framerate=%d" % (framerate))
    # print("nframes=%d" % (nframes))
 
    str_data = f.readframes(nframes)
    f.close()  # 將波形資料轉換成陣列
    # Cutnum =nframes/framerate/CutTimeDef
    # 需要根據聲道數和量化單位，將讀取的二進位制資料轉換為一個可以計算的陣列
    wave_data = np.frombuffer(str_data, dtype=np.short)
    remainder = len(wave_data) % 2
    if remainder != 0:
       wave_data = np.resize(wave_data, len(wave_data) + remainder)
    wave_data.shape = -1, 2
    wave_data = wave_data.T
    temp_data = wave_data.T
    # StepNum = int(nframes/200)
    StepNum = CutFrameNum
    StepTotalNum = 0
    haha = 0
    while StepTotalNum < nframes:
        # for j in range(int(Cutnum)):
        # print("Stemp=%d" % (haha))
        SaveFile = "%s-%03d.wav" % (FileName, (haha+1))
        # print(WavName)
        if haha % 3==0:
          print("*",end='')
        temp_dataTemp = temp_data[StepNum * (haha):StepNum * (haha + 1)]
        haha = haha + 1
        StepTotalNum = haha * StepNum
        temp_dataTemp.shape = 1, -1
        temp_dataTemp = temp_dataTemp.astype(np.short)  # 開啟WAV文件
        f = wave.open(target_path+SaveFile, "wb")
        # 配置聲道數、量化位數和取樣頻率
        f.setnchannels(nchannels)
        f.setsampwidth(sampwidth)
        f.setframerate(framerate)
        # 將wav_data轉換為二進位制資料寫入檔案
        f.writeframes(temp_dataTemp.tobytes())
        f.close()
 
 

 
def texts_to_one(path):
    files = os.listdir(path)
    files.sort()
    files = [path+"\\" + f for f in files if f.endswith(".txt")]
    string = ""
    for file in files:
        with open(file, "r", encoding='utf-8') as f2:
            txt= f2.read().split("\n")
            if len(txt) < 2:
                continue
            
            string = string+txt[1]
    return string
 
 


def VoiceToText_thread(file):
  txt_file = "%s/%s.txt" % (txt_path, file[:-4])
      
  if os.path.isfile(txt_file):
    return
  with open("%s/%s.txt" % (txt_path, file[:-4]), "w", encoding="utf-8") as f:
    f.write("%s:\n" % file)
    r = sr.Recognizer()  # 預設辨識英文
    with sr.WavFile(wav_path+"/"+file) as source:  # 讀取wav檔
      audio = r.record(source)
      # r.adjust_for_ambient_noise(source)
      # audio = r.listen(source)
    try:
      text = r.recognize_google(audio,language = voiceLanguage)
      text = chinese.s2t(text)
      # r.recognize_google(audio)
      
      if len(text) == 0:
        print("===無資料==")
        return

      print(f"{file}\t{text}")
      f.write("%s \n\n" % text)
      if file == files[-1]:
          print("結束翻譯")
    except sr.RequestError as e:
      print("無法翻譯{0}".format(e))
      # 兩個 except 是當語音辨識不出來的時候 防呆用的
      # 使用Google的服務
    except LookupError:
      print("Could not understand audio")
    except sr.UnknownValueError:
      print(f"Error: 無法識別 Audio\t {file}")
  

def convert(mp3file):
   

  #@markdown 錄音檔的位置
  mp3Name= 'uploads\\'+mp3file #@param {type:"string"}



  workpath = os.getcwd()

  WavName = mp3Name[:mp3Name.rfind(".")]+".wav"
  global FileName 
  FileName = mp3Name[mp3Name.rfind("\\")+1:mp3Name.rfind(".")]
  print('FileName',FileName)
  print('WavName',WavName)
  os.chdir(workpath)
  #@markdown 若 wav_path, txt_path 目錄存在是否移除重建
  # chk='y' #@param ["y","n"]
  

  print('workpath',workpath)
  print('mp3name',mp3Name)
  print('WavName',WavName)
  print(" mp3 轉 wav 檔 ".center(100,'=')) 
  print('{} -i "{}" -f wav "{}"'.format("ffmpeg",workpath+'\\'+mp3Name, workpath+'\\'+WavName))
  os.system('{} -i "{}" -f wav "{}"'.format("ffmpeg",workpath+'\\'+mp3Name, workpath+'\\'+WavName))

  print(" Wav 檔名為 {} ".format(WavName).center(96))
  reset_dir(wav_path)
  reset_dir(txt_path)
  # Cut Wave Setting

  print(" 音頻以每{}秒分割 ".format(CutTimeDef).center(94,'='))
  CutFile(workpath+'\\'+WavName, workpath+'\\'+wav_path)
  print("")
  print(" 完成分割 ".center(100,'-'))
  global files
  files = os.listdir(wav_path) 
  files.sort()

  with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
      executor.map(VoiceToText_thread, files)
  # VoiceToText_thread(files)
  # VoiceToText_thread(wav_path, files, txt_path)
  now = datetime.now()
  meeting_time = "{}-{}-{}".format(now.date(),now.hour,now.minute)
  # texts_to_one(txt_path, target_txtfile)

  # shutil.rmtree(wav_path)
  # shutil.rmtree(txt_path)
  
  # os.remove(mp3Name)
  os.remove(WavName)
  reset_dir(wav_path)
  # reset_dir(txt_path)
  return txt_path,meeting_time