import os
import requests
import json
import time
import pandas as pd
import random
import base64
from fpdf import FPDF
import yaml
import streamlit as st
from transformers import pipeline, set_seed
from bad_words import var_list
from nltk.stem import PorterStemmer

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing


MAX_IMAGES = 4
URL_CONVERT = "https://play.ht/api/v1/convert"
URL_GET_AUDIO = "https://play.ht/api/v1/articleStatus"
#USER_ID = 'e3KRfjvXUgZN3LoA1DzYlXpJdmC2'
MAX_ATTEMPTS = 60
LAG = 1

def chunk(lst, n):
    for x in range(0, len(lst), n):
        e_c = lst[x : n + x]

        #if len(e_c) &lt; n:
        #    e_c = e_c + [None for y in range(n - len(e_c))]
        yield e_c


def postprocess_text(text):
   
    text = text.replace('\n\n', '\n')
    #print(text)
    words_list = text.split(" ")
    #print(words_list)
    parts_list = list(chunk(words_list, 30))
    #print(parts_list)
    parts_str = [" ".join(part) for part in parts_list]
    #print(parts_str)
    result = "\n".join(parts_str) 
    #print(result)
    return result


def process_fairy_tales_dataset(dataset_path, dataset_file):
    with open(os.path.join(dataset_path, dataset_file), encoding="utf-8") as f:
          read_data = f.read()
    tales = read_data.split('\n\n\n\n') 
    #print(len(tales))
    n = len(tales)
    name_stories = []
    for i in range(n):
        #print(i)
        temp = tales[i].strip().split("\n\n")
        filter(lambda x: len(x) > 1, temp)
        name_of_story = temp[0].strip()
        if len(name_of_story) < 100 and name_of_story.find('NOTES') and len(name_of_story) > 1:
              #print(i)
              #print(name_of_story)
              name_stories.append(name_of_story)
        #tales_dict.update({})
    sprev = 0
    tales_dict = {}
    tales_dict.update({})
    titles = []
    stories = []

    result_path = os.path.join(dataset_path, "tales.txt")
    with open(result_path, 'w', encoding='utf-8') as r:
        for name in name_stories[1:]:
            s = read_data.find(name)
            if s == -1:
                break
            story = read_data[ sprev: s]
            sprev = s
            temp = story.strip().split("\n\n")
            #print(temp[0])

            text_story = "\n".join(temp[1:])
            tales_dict.update({temp[0] : text_story})
            r.write(temp[0] + '\n\n' + text_story + "<EOS>" + '\n\n************************************\n')
            titles.append(temp[0])
            stories.append(text_story)
        # print(temp)

      
    csv_path = os.path.join(dataset_path, "tales.csv")
    df = pd.DataFrame(columns = ["title", "story"])
    df['title'] = titles
    df['story'] = stories
    df.to_csv(csv_path, sep='\t')
    #print(df.head())    
    return titles, stories, df
    

def get_audio(sound_provider, text, voice, API_KEY, USER_ID):
    if sound_provider == 'Play.ht':
                payload = json.dumps({
                      "voice": voice,
                      "content": [text],
                      "title": ""
                })
                headers = {
                     'Authorization': API_KEY,
                     'X-User-ID': USER_ID,
                     'Content-Type': 'application/json'
                }

                response = requests.request("POST", url = URL_CONVERT, headers=headers, data=payload)
                result = response.json()
                transcriptionId = result['transcriptionId']
                #result = json.loads(json_ob)
                print(transcriptionId)

                url = "https://play.ht/api/v1/articleStatus" + f"?transcriptionId={transcriptionId}"
            #     print(url)
                filename = 'tale.mp3'
                for i in range(MAX_ATTEMPTS):
                    response = requests.get(url, headers = headers)
                    result = response.json()
                    status = result['converted']
                    print(status)
                    if status == True:
                      file_url = result['audioUrl']
                      r = requests.get(file_url)
                      with open(filename, 'wb') as f:
                           f.write(r.content)
                           return 0, filename
                      time.sleep(LAG)
                return -1, None
    elif sound_provider == 'Amazon':
                session = Session(aws_access_key_id=USER_ID,
                                  aws_secret_access_key=API_KEY, region_name="us-east-1")
                polly = session.client("polly")
                try:
                    # Request speech synthesis
                    response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                                       VoiceId=voice)
                    print(response)
                except (BotoCoreError, ClientError) as error:
                    # The service returned an error, exit gracefully
                    print(error)
                    return -1, None
                # Access the audio stream from the response
                if "AudioStream" in response:
                    with closing(response["AudioStream"]) as stream:
                        output = "tale.mp3"
                        try:
                            with open(output, "wb") as file:
                                #file.write(stream.read())
                                result = stream.read()
                            return 0, result

                        except IOError as error:
                            print(error)
                            return -1, None
                else:
                    # The response didn't contain audio data, exit gracefully
                    print("Could not stream audio")
                    return -1, None

    else:
        return -1, None


def get_images_tale(tale, title):
   summarizer = pipeline("summarization")
   sentences = tale.split(". ")
   n = len(sentences)
   print('len', n)
   part = n // MAX_IMAGES
   #len_parts = [part] * (MAX_IMAGES - 1) + [MAX_IMAGES]
   #result  = [sentences[min(i * part + random.randint(0, len_parts[i] - 1), n - 1)] for i in range(MAX_IMAGES)]
   #result[0] = sentences[0]
   tale_parts = [". ".join(sentences[i * part : i * part + part]) + ". " for i in range(MAX_IMAGES)]
   i = MAX_IMAGES - 1
   tale_parts.append(". ".join(sentences[i * part + part : ]) + ". " )
   main_sents = []
   for part in tale_parts:
      summary=summarizer(part, max_length=20, min_length=5, do_sample=False)[0]
      temp = summary['summary_text']
      main = list(temp.split("."))[0]
      main_sents.append("Make illustration of " + " " + main.lower())
   image_names = []
   for i in range(len(main_sents)):
      r = requests.post(url='https://hf.space/embed/valhalla/glide-text2im/+/api/predict/',  json={"data": [main_sents[i]]})
      #print(r)
      encoding = r.json()['data'][0][22:]
      image_64_decode = base64.b64decode(encoding)
      image_result = open(f'image{i}.png', 'wb') # create a writable image and write the decoding result
      image_result.write(image_64_decode)
      image_names.append(f'image{i}.png')
   return image_names, tale_parts


def add_text(text, pdf):
    #pdf.add_page()
    pdf.set_font("Arial", size=12)
    #lines = text.split(".")
    #print(len(lines))
    #for line in lines:
    pdf.multi_cell(200, 10, txt=text,  align="L")


def add_image(image_path, pdf):
    pdf.image(image_path, x = 60,  w = 60, type = 'PNG')
    #pdf.set_font("Arial", size=12)
    #pdf.ln(85)  # ниже на 85
    #pdf.cell(200, 10, txt="{}".format(image_path), ln=1)



def create_pdf(title, texts, image_names):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    print(title)
    #pdf.cell(200, 10, txt=title, border = 1, ln = 1, align="C")
    print('start')
    for i in range(len(image_names)):
        add_text(texts[i], pdf)
        add_image(image_names[i], pdf)
    add_text(texts[len(texts)-1], pdf)
    pdf.output("output.pdf")
    with open("output.pdf", 'rb') as f:
        data = f.read()
    return data

# def create_pdf(texts):
#     pdf = FPDF()
#     for i in range(len(texts)):
#         add_text(texts[i], pdf)
#         #add_image(image_names[i], pdf)
#     pdf.output("output.pdf")
#     with open("output.pdf", 'rb') as f:
#         data = f.read()
#     return data

@st.cache
def read_keys():
    # Read YAML file
    with open("conf.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded['userid_playht'], data_loaded['userid_amazon']

@st.cache
def read_voices(sound_provider):
    if sound_provider == 'Amazon':
        voices = pd.read_csv("voices_amazon.csv", sep = ";")
    else:
        voices = pd.read_csv("voices_playht.csv", sep=";")
    voice_ids = voices['voice_id'].values.tolist()
    voice_names = voices['voice_name'].values.tolist()
    return voice_ids, voice_names


def get_sentiment(tale):
    classifier = pipeline('sentiment-analysis', max_length=512, truncation=True)
    result = classifier(tale)
    return result

def get_love_mood(tale):
    tale_list = list(tale.split(" "))
    root_words = []
    ps = PorterStemmer()
    for w in tale_list:
         rootWord = ps.stem(w)
         root_words.append(rootWord)


    for word in var_list:
        if word in root_words:
            print(f"bad****{word}*****")
            return True, word
        if tale.find(" " + word + " ") != -1:
            print(f"bad****{word}*****")
            return True, word
    return False, ""
