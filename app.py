from flask import Flask, Response, request, jsonify
from dops.functions import *
import base64
import requests
import sys
import numpy as np
import pandas as pd
import openai
import uuid
import os
import random
from dops.classes import Example, GPT, FairyTaleGenerator
from prompts import var_dict

userid_playht, userid_amazon = read_keys()
key_openai, key_playht, key_amazon = os.environ['KEY_OP'], os.environ['KEY_PLAY'], os.environ['KEY_AMAZON']

app = Flask(__name__)

@app.route('/')
def index():
        return 'Fairy Tales API'


@app.route('/api/v1/audio/', methods=['GET', 'POST'])
def get_audio_request():
        tale = request.args.get('tale')
        voice_name = request.args.get('voice')
        sound_provider = request.args.get('sound_provider')
        print(tale, voice_name, sound_provider)
        voice_ids, voice_names = read_voices(sound_provider)
        if sound_provider == 'Amazon':
                print("1")
                key_sound = key_amazon
                user_id_sound = userid_amazon
                print(voice_names, key_sound, user_id_sound)
        else:
                print("2")
                key_sound = key_playht
                user_id_sound = userid_playht
        print(key_sound, user_id_sound)
        print(voice_name)
        index = voice_names.index(voice_name)
        voice_id = voice_ids[index]
        status, data = get_audio(sound_provider, tale, voice_id, key_sound, user_id_sound)
        print(status)
        return Response(data, mimetype="audio/x-mpeg-3")



@app.route('/api/v1/tale', methods=['GET', 'POST'])
def get_text():
      story_prompt = request.args.get('prompt')
      analyse_flag = request.args.get('analyse_flag')
      print(story_prompt)
      print(analyse_flag)
      ftg = FairyTaleGenerator(key_openai, "tales5.csv")
      responce = ftg.get_one_tale(story_prompt).replace("output:", "").strip()
      if analyse_flag == "True":
            sentiment = get_sentiment(responce)
            love_mood, bad_word = get_love_mood(responce)
            return jsonify(tale=responce, sentiment=sentiment, love_mood=love_mood, bad_word=bad_word)
      else:
            return jsonify(tale=responce)



# @app.route('/image', methods=['GET', 'POST'])
# def get_image():
#     #     tale = request.args.get('tale')
#     #     sentences = tale.split(".")
#     #     print(sentences[0])
#     #     r = requests.post(url='https://hf.space/embed/valhalla/glide-text2im/+/api/predict/', \
# 	# json={"data": [sentences[0]]})
#     #     encoding = r.json()['data'][0][22:]
#     #     image_64_decode = base64.b64decode(encoding)
#         prompts = ['princess']
#         get_images(prompts)
#         with open("temp0.jpg", "rb") as f:
#              data = f.read()
#
#         return Response(data, mimetype="image/gif")


if __name__ == "__main__":

    app.run(port = 5000)