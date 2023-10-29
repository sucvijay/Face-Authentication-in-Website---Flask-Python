import json
import sqlite3

from flask import Flask, request, render_template, send_from_directory, redirect
import face_recognition as fr
import cv2
import numpy as np
import os
from flask_cors import CORS
import base64
from io import BytesIO

from werkzeug.utils import secure_filename

from db import user



app = Flask(__name__)
CORS(app)


known_names = []
known_name_encodings = []
path = "./train/"

images = os.listdir(path)
for _ in images:
    if _ == ".DS_Store":
        continue
    image = fr.load_image_file(path + _)
    image_path = path + _
    encoding = fr.face_encodings(image)[0]
    known_name_encodings.append(encoding)
    known_names.append(os.path.splitext(os.path.basename(image_path))[0].capitalize())

print(known_names)
#
# #
#
# test_image = "test.jpg"
# image = cv2.imread(test_image)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# face_locations = fr.face_locations(image)
# face_encodings = fr.face_encodings(image, face_locations)
#
# for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#     matches = fr.compare_faces(known_name_encodings, face_encoding)
#     name = ""
#
#     face_distances = fr.face_distance(known_name_encodings, face_encoding)
#     best_match = np.argmin(face_distances)
#
#     if matches[best_match]:
#         name = known_names[best_match]
#         print(name)
#
#     cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
#     cv2.rectangle(image, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
#     font = cv2.FONT_HERSHEY_DUPLEX
#     cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#
# cv2.imwrite("./output.jpg", image)

@app.route("/forgot", methods=["GET"])
def forgot():
    return render_template("forgot.html")

@app.route("/register")
def reg():
    return render_template("register.html")





def b64toimg(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


@app.route("/", methods=["GET"])
def redirect_external():
    return render_template("index.html")





@app.route("/create",methods=["POST"])
def create():
    data = request.form.to_dict()
    print(data)
    file = request.files['file'].read()
    npimg = np.fromstring(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    face = fr.face_encodings(img)
    
    conn = sqlite3.connect("sqlite.db", check_same_thread=False)
    query = f'insert into users (fname,lname,email,registerNo,pass,confPass) values("{data.get("fName")}","{data.get("lName")}","{data.get("email")}","{data.get("registerNo")}","{data.get("password")}","{data.get("confirmPassword")}");'
    # print(query)
    id = conn.cursor().execute(query)

    # users = connection.execute("select * from users;").fetchall()

    # print(users)

    conn.commit()
    conn.close()
    
    cv2.imwrite("./train/"+str(id.lastrowid)+".jpg", img)

    # cuser = user.insert_one(data)
    # cv2.imwrite("./train/"+str(cuser.inserted_id)+".jpg", img)

    

    known_name_encodings.append(face[0])
    # known_names.append(str(cuser.inserted_id))
    
    known_names.append(str(id.lastrowid))
    

    return redirect("/index.html",code=302)

@app.route("/profile",methods=["POST"])
def login():
    data=request.form.to_dict()

    b64 = data["imgdata"]
    del data["imgdata"]

    # print(data)

    # fuser = user.find_one(data)
    
    
    query = f'select * from users where email = "{data.get("email")}" and pass = "{data.get("password")}";'
    
    conn = sqlite3.connect("sqlite.db", check_same_thread=False)
    
    res = conn.execute(query).fetchone()
    
    conn.close()
    
    print(res)
    
    fuser = {}
    
    if(res==None) : return "Wrong Password"

    fid = str(res[0])
    image = b64toimg(b64)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = fr.face_locations(image)
    face_encodings = fr.face_encodings(image, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = fr.compare_faces(known_name_encodings, face_encoding)
        name = ""
        face_distances = fr.face_distance(known_name_encodings, face_encoding)
        best_match = np.argmin(face_distances)


        if matches[best_match]:
            name = known_names[best_match]
            print("name = " + name)

        if(name==fid):
            fuser["Full Name"] = res[1]+" "+res[2]
            fuser["email"] = res[3]
            fuser["registerNo"] = res[4]


            return render_template("profile.html",data=fuser, userid = fid)
        else:
            return "Not Match"
    return "Please try again"

@app.route('/img/<path:path>')
def sendimage(path):
    return send_from_directory('train', path)

@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('templates', path)

