from re import template
from MySQLdb import Timestamp
import cv2
import numpy as np
import face_recognition
import os
from datetime import date, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from flask import Flask, redirect, url_for, render_template, request, flash
#from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

path='training'#/Microsoft/training
images=[]
imgLabel=[]
mylist=os.listdir(path)

for cl in mylist:
    curimg=cv2.imread(f'{path}\\{cl}')
    images.append(curimg)
    imgLabel.append(os.path.splitext(cl)[0])

def find_Encoding(images):
    encodLst=[]
    for img in images:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodLst.append(encode)
    return encodLst

encode_Faces=find_Encoding(images)


def Recognize(name,visit_date, visit_time):
     connection=mysql.connector.connect(host="localhost", database="face_data", user="root",passwd="My.sql7890")
     mysql_insert_query="INSERT INTO Patient(name, visit_date, visit_time) VALUES (%s,%s,%s)"  
     cursor=connection.cursor()
     values=(name, visit_date, visit_time)
     cursor.execute(mysql_insert_query,values)
     connection.commit()
     cursor.execute("SELECT * FROM Patient")
     myresult=cursor.fetchall()
     for i in myresult:
         print(i)
     cursor.close();

@app.route('/test')
def test():
    webcam=cv2.VideoCapture(0)
    nm="a"

    while True:
        success, img=webcam.read()
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

        faceCurFrm= face_recognition.face_locations(imgS)
        encodeCurFrm=face_recognition.face_encodings(imgS,faceCurFrm)

        for encodFace, faseLocation in zip(encodeCurFrm,faceCurFrm):
            maches=face_recognition.compare_faces(encode_Faces,encodFace)
            faceDis=face_recognition.face_distance(encode_Faces,encodFace)
        
            machesIndex=np.argmin(faceDis)

            if maches[machesIndex]:
                name = imgLabel[machesIndex].upper()
             # print(name)
                y1,x2,y2,x1=faseLocation
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),3)
                cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX ,1,(255,255,255),2)
            
                
                vtime=datetime.now().time()
                vdate=datetime.now().date()
                if name!=nm:
                    Recognize(name,str(vtime),str(vdate))
                    nm=name
    
    
        cv2.imshow('Frame',img)
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    webcam.release()
    cv2.destroyAllWindows()
    return render_template('index.html')
if __name__ == "__main__":
        app.run(debug=True)