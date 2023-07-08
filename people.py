import numpy as np
import tensorflow.compat.v1 as tf
import cv2
import time
import datetime
import os
import csv
import requests


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name(
            'image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name(
            'detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name(
            'detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name(
            'detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name(
            'num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores,
                self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0, i, 0] * im_height),
                             int(boxes[0, i, 1]*im_width),
                             int(boxes[0, i, 2] * im_height),
                             int(boxes[0, i, 3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()

# 回傳辦公室人數
class Office_People:
    def __init__(self):
        self.num_of_people = 0
        current_minute = datetime.datetime.now().minute
        
    def set_office_people(self, value):
        self.num_of_people = value
    
    # 及時回傳人數
    def get_office_people(self):
        return self.num_of_people
    
    # 每分鐘寫到一個新的csv檔
    def write_num_of_people_to_csv(self):
        self.csv_writer.write_value(self.num_of_people)
    
    # 初始化
    def start_csv_writing(self):
        self.csv_writer = CSVWriter('people_data\office_people_data')

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
    
    # 辦公室人數初始化
    office_people = Office_People()
    office_people.start_csv_writing()
    
    
    cap = cv2.VideoCapture(0) 
    model_path = 'ssd_inception_v2_coco_2017_11_17/frozen_inference_graph.pb'

    odapi = DetectorAPI(path_to_ckpt=model_path)
    # 信心值
    threshold = 0.5
    # 輸出視訊檔案相關設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_filename = "output.mp4"
    output_fps = 30.0
    output_resolution = (1280, 720)
    out = cv2.VideoWriter(output_filename, fourcc, output_fps, output_resolution)
    enter_count = 0
    exit_count = 0
    prev_direction = None
    list_X = []
    while True:
        # r表示影像是否擷取成功、img表示擷取的影像
        r, img = cap.read()
        # 擷取失敗，跳出while迴圈
        if r == False:
            break

        img = cv2.resize(img, (1280, 720))
        # detect
        boxes, scores, classes, num = odapi.processFrame(img)
        # 獲取影像寬度和高度
        height, width, _ = img.shape
        # 計算畫面中心點的像素坐標
        center_x = width // 2
        # Visualization of the results of a detection.
        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes[i]
                # 將偵測到的人框起來
                cv2.rectangle(img, (box[1], box[0]),
                              (box[3], box[2]), (255, 0, 0), 2)
                # 藍色框框左上角文字
                cv2.putText(
                    img, f'person {i+1}', (box[1], box[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                # add list
                centerX = (box[1]+box[3])/2
                list_X.append(centerX)

        # 計算進出人數
        if len(list_X) >= 2:
            current_direction = 'Enter' if list_X[0] < list_X[1] else 'Exit'

            if prev_direction is None:
                prev_direction = current_direction

            if current_direction=='Enter' and  prev_direction == 'Enter' and list_X[0]<center_x and list_X[1]>center_x:
                enter_count += 1
            elif current_direction=='Exit' and  prev_direction == 'Exit' and list_X[0]>center_x and list_X[1]<center_x:
                exit_count += 1

            prev_direction = current_direction
            list_X.pop(0)

        # 顯示進出人數
        cv2.putText(img, f'Enter count: {enter_count}', (40, 80),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
        if len(list_X)>0:
            cv2.putText(img, f'Exit count: {exit_count}', (40, 120),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
        
        people_data = {"people": office_people.get_office_people()}
        response = requests.post("http://localhost:8000/peopleData/", json=people_data)            
                    
        # 辦公室人數
        office_people.set_office_people(enter_count-exit_count)
        # print(office_people.get_office_people())
        office_people.write_num_of_people_to_csv()
        
        
        out.write(img)
        # cv2.imshow("detect", img)
        key = cv2.waitKey(1)
        # 按下小q退出while迴圈
        if key & 0xFF == ord('q'):
            break
            
        time.sleep(0.1)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
