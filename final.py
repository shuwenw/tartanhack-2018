from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  
import cv2
import numpy as np
import time 
import requests
from os.path import expanduser 
import copy

ITER = 40

cap = cv2.VideoCapture(1) #usb 1


def seperator(string):
    result=copy.deepcopy(string)
    count=0
    for i in range(len(string)):
        if count>30 and string[i]==" ":
            result=result[:i]+"\n"+result[i+1:]
            count=0
        count+=1
    return (result)


def drawRec(x, y):
    cv2.rectangle(img,(x-50, y-50),(x+50, y+50), (255,255,255), 5)
    
def label(string1, confidence, x, y):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_appear = string1 + ", " + confidence
    cv2.putText(img, text_appear, (x-50, y+75), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

# enable browser logging
d = DesiredCapabilities.CHROME
d['loggingPrefs'] = { 'browser':'ALL' }
driver = webdriver.Chrome("./chromedriver")
# load some site
driver.get('localhost:8000')
# print messages

string1 = "a"
confidence = "C"
x = 640
y = 500
counter = 0
x_sum = 0
y_sum = 0

# import cv2
# x = 0
# y = 0
# h = 100
# w = 100
# img = cv2.imread("cat.jpg")
# crop_img = img[y:y+h, x:x+w]
# cv2.imwrite("crop.jpg", crop_img)

def detec_text(img, x, y):
    a = time.time()


    crop_img_txt = img[max(y-300, 0):min(720, y+300), max(x-300, 0):min(1280, x+300)]

    cv2.namedWindow('c-image-t',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('c-image-t', 300,300)

    cv2.imwrite("./image/crop_txt.jpg", crop_img_txt)

    subscription_key = "a712d89988794d90b1a92b91d6921a5e"
    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
    ocr_url = vision_base_url + "ocr"


    image_path = expanduser("./image/crop_txt.jpg")

    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key, 
                  "Content-Type": "application/octet-stream" }
    params     = {'language': 'unk'}
    response   = requests.post(ocr_url, 
                               headers=headers, 
                               params=params, 
                               data=image_data)

    response.raise_for_status()

    analysis = response.json()

    line_infos = [region["lines"] for region in analysis["regions"]]
    sentences = []
    for line in line_infos:
        words_for_line = []
        for word_metadata in line:
            for word_info in word_metadata["words"]:
                    words_for_line.append(word_info["text"])
        sentences.append(" ".join(words_for_line))

    allwords = "\n\n".join(sentences)
    b = time.time()
    txt_result = seperator(allwords).encode('utf-8')
    print(txt_result)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(crop_img_txt, "txt_result is:\n"+ str(txt_result), (50, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("c-image-t", crop_img_txt)


    print("Detection took: ", b-a, "(s).")
    return("Text detection complete")


def detec(img, x, y):
    a = time.time()


    crop_img = img[max(y-300, 0):min(720, y+300), max(x-300, 0):min(1280, x+300)]

    cv2.namedWindow('c-image',cv2.WINDOW_NORMAL)
    cv2.imshow("c-image", crop_img)
    cv2.resizeWindow('c-image', 300,300)

    cv2.imwrite("./image/crop.jpg", crop_img)
    subscription_key = "a712d89988794d90b1a92b91d6921a5e"
    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
    vision_analyze_url = vision_base_url + "analyze"
     
    #~/Desktop/image/cat.jpg
    image_path = expanduser("./image/crop.jpg")

    image_data = open(image_path, "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key, 
                  "Content-Type": "application/octet-stream" }
    params     = {'visualFeatures': 'Categories,Tags', 'details': 'landmarks,celebrities'}
    response   = requests.post(vision_analyze_url, 
                               headers=headers, 
                               params=params, 
                               data=image_data)

    response.raise_for_status()

    analysis = response.json()
    #print(analysis)

    image_tags = [tag["name"] for tag in analysis["tags"] if tag["confidence"] > 0.9]
    print(image_tags)

    #best_tag = max(analysis["tags"], key=lambda tag: tag["confidence"])
    #print(best_tag["name"],", confidence:", best_tag["confidence"])

    for category in analysis["categories"]:
        landmarks = category.get("detail", {}).get("landmarks", [])
        for landmark in landmarks:
            if landmark["confidence"] > 0.8:
                print(landmark["name"])

    b = time.time()

    print("Detection took: ", b-a, "(s).")
    return (image_tags)




# def detec(img, x, y):

while(1):
    ret, img = cap.read()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    if cv2.waitKey(25) & 0xFF == ord("t"):
        result_name = detec_text(img, int(x), int(y))
        confidence = "Confidence unknown!" 

    if cv2.waitKey(25) & 0xFF == ord(' '):
        result_name = detec(img, int(x), int(y))
        string1 = ""
        for i in result_name:
            string1 += (i + " . ")
        confidence = "Confidence > 80%" 

    for entry in driver.get_log('browser'):
        msg = entry['message']
        _first = msg.find('\"')
        _second = msg.find('\"', _first+1)
        _comma = msg.find(", ")
        pred_x = msg[_first + 1: _comma]
        pred_y = msg[_comma + 2: _second]
        if (_comma != -1 and _first != -1 and _second != -1):
            if (pred_x == 'a patchresponse was monotone'): continue
            x_temp = int(float(pred_x))
            x_sum += x_temp
            y_temp = int(float(pred_y))
            y_sum += y_temp
            counter += 1
            print(x, y)
            if (counter == ITER):
                x = x_sum / ITER
                y = (y_sum / ITER) /7 * 10
                x_sum = 0
                y_sum = 0
                counter = 0

    drawRec(int(x), int(y))
    label(string1, confidence, int(x), int(y))
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    cv2.imshow("image", img)
    cv2.resizeWindow('image', 1280,720)

cap.release()
cv2.destroyAllWindows()

# "http://localhost:8000/WebGazer%20Demo_files/webgazer.js 10750:20 "418, 642" 1518277910191"