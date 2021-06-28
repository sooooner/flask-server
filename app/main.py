from werkzeug.utils import secure_filename
from flask import Flask, render_template, request

import cv2
import json
import pymysql
import requests
import numpy as np
import matplotlib.pyplot as plt

def anchor_to_coordinate(box):    
    x1 = box[0] - box[2]/2
    x2 = box[0] + box[2]/2
    y1 = box[1] - box[3]/2
    y2 = box[1] + box[3]/2
    return (x1, x2, y1, y2)

def db_uploader(file_name):
    creat_test_img_sql = '''
    CREATE TABLE IF NOT EXISTS test_img (
    id INT(11) NOT NULL AUTO_INCREMENT,
    file_name VARCHAR(30) NOT NULL,
    PRIMARY KEY (id)
    );
    ''' 
    conn = pymysql.connect(host='mysql', user='root', charset='utf8') 
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'CREATE DATABASE IF NOT EXISTS dacon;'
    cursor.execute(sql) 

    sql = "USE dacon;" 
    cursor.execute(sql) 
    sql = f"INSERT INTO test_img (file_name) VALUES ('{file_name}');"
    cursor.execute(sql)
    conn.commit()

# def object_detection(file_name):
#     global model
#     image_path = './static/uploads/'
#     img = cv2.imread(image_path + file_name)
#     img = np.expand_dims(cv2.resize(img, dsize=(768,432))/255, axis=0)

#     data = json.dumps({"signature_name": "serving_default", "instances": img.tolist()})

#     headers = {"content-type": "application/json"}
#     # json_response = requests.post('http://host.docker.internal:8501/v1/models/frcnn:predict', data=data, headers=headers)
#     json_response = requests.post('http://172.17.0.1:8501/v1/models/frcnn:predict', data=data, headers=headers)
#     # # json_response.text

#     predictions = json.loads(json_response.text)['predictions']

#     max_output_size = 3
#     img = img[0].numpy().copy()

#     scores_order = np.argsort(predictions[0]['output_1'], axis=0)[::-1]
#     boxes = np.squeeze(np.take(predictions[0]['output_2'], scores_order, axis=0))
#     boxes = boxes[boxes[:, 2] > 16]
#     boxes = boxes[boxes[:, 3] > 16][:max_output_size]
#     boxes = np.mean(boxes, axis=0)

#     anchor = anchor_to_coordinate(boxes.numpy())
#     cv2.rectangle(
#         img, 
#         (int(anchor[0]), int(anchor[2])), (int(anchor[1]), int(anchor[3])), 
#         (1, 0, 0), 
#         thickness=1
#     )

#     plt.imshow(img)
#     plt.axis('off')
#     plt.savefig(f'./static/detect/{file_name}', dpi=200)

def object_detection(file_name):
    global model
    image_path = './static/uploads/'
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)

    data = json.dumps({"signature_name": "serving_default", "instances": img.tolist()})

    headers = {"content-type": "application/json"}
    # json_response = requests.post('http://host.docker.internal:8501/v1/models/frcnn:predict', data=data, headers=headers)
    json_response = requests.post('http://172.17.0.1:8501/v1/models/frcnn:predict', data=data, headers=headers)
    # # json_response.text

    predictions = json.loads(json_response.text)['predictions']

    img_ = img[0].copy()
    for anchor in predictions:
        ymin, xmin, ymax, xmax =anchor
        ymin *= img_.shape[0]
        ymax *= img_.shape[0]
        xmin *= img_.shape[1]
        xmax *= img_.shape[1]
        cv2.rectangle(
            img_, 
            (int(xmin), int(ymin)), (int(xmax), int(ymax)), 
            (0, 0, 255), 
            thickness=2
        )

    plt.imshow(img_)
    plt.axis('off')
    plt.savefig(f'./static/detect/{file_name}', dpi=200)

app = Flask(__name__)
@app.route('/')
def home():
    return render_template("home.html")

@app.route("/loading_page", methods = ['GET', 'POST'])
def loading():
    if request.method == 'POST':
        global file_name
        f = request.files['file1']
        file_name = secure_filename(f.filename)
        db_uploader(file_name)
        f.save(f'static/uploads/{file_name}')
        return render_template("loading_page.html")

@app.route('/file_uploaded', methods = ['GET', 'POST'])
def upload_file():
    # if request.method == 'POST':
    global file_name
    f = file_name
    object_detection(f)
    return render_template("image.html", img=f)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)