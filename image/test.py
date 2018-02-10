import time 
import requests
import copy
from os.path import expanduser 


def seperator(string):
    result=copy.deepcopy(string)
    count=0
    for i in range(len(string)):
        if count>30 and string[i]==" ":
            result=result[:i]+"\n"+result[i+1:]
            count=0
        count+=1
    return (result)
    
    
subscription_key = "a712d89988794d90b1a92b91d6921a5e"
assert subscription_key
vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
ocr_url = vision_base_url + "ocr"


image_path = expanduser("~/Desktop/image/word.jpg")

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
print(seperator(allwords).encode('utf-8'))
