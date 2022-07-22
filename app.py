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



sound_provider = "Amazon"
userid_playht, userid_amazon = "", ""
key_openai, key_playht, key_amazon = "", "", ""
voice_ids, voice_names = [], []
KEY = "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"

app = Flask(__name__)

@app.route('/')
def hello_world():
        return 'Hello Sammy!'




@app.route('/audio', methods=['GET', 'POST'])
def get_audio_request():
        tale = request.args.get('tale')
        voice_name = request.args.get('voice')
        service_provider = request.args.get('service_provider')
        print(tale, voice_name, sound_provider)

        if sound_provider == 'Amazon':
                key_sound = key_amazon
                user_id_sound = userid_amazon
        else:
                key_sound = key_playht
                user_id_sound = userid_playht
        print(voice_names)

        index = voice_names.index(voice_name)
        voice_id = voice_ids[index]
        status, data = get_audio(sound_provider, tale, voice_id, key_sound, user_id_sound)
        print(status)
        return Response(data, mimetype="audio/x-mpeg-3")



@app.route('/tale', methods=['GET', 'POST'])
def get_text():
      story_prompt = request.args.get('prompt')
      print(story_prompt)
      #ftg = FairyTaleGenerator(key_openai, "tales5.csv")
      #responce = ftg.get_one_tale(story_prompt).replace("output:", "").strip()
      responce = "The kingdom of Ayland was in turmoil. The king and queen had died, leaving behind them a young daughter, Princess Aurora. Aurora was only six years old when her parents\
        died, and so the kingdom was left in the care of her uncle, Duke Henry.\
        Duke Henry was a kind man, and he loved his niece dearly. But he was also\
        a ambitious man, and he had his sights set on the throne. So when it became clear that the people of Ayland would not accept him as their king, he\
        hatched a plan to get rid of Princess Aurora.\
        He had a tower built in the middle of the forest, and he had Aurora locked away inside it. The only person\
        who was allowed to visit her was her nurse, who brought her food and supplies.\
        Phillip returned the next day with a ladder. He climbed up to the window and helped Aurora down.\
        They rode off into the sunset, and they lived happily ever after."
      print("generate")
      #print(responce)
      sentiment = get_sentiment(responce)
      love_mood, bad_word = get_love_mood(responce)
      return jsonify(tale=responce, sentiment=sentiment, love_mood=love_mood, bad_word=bad_word)

    # prompt = request.args.get('prompt')
        # print(prompt)
        # ftg = FairyTaleGenerator(KEY, "./tales.csv")
        # tales = ftg.get_many_tales([prompt])
        # tale = tales[0]
        # return Response(tale, mimetype = "text/plain")


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



#serve(app, host='0.0.0.0', port=8080, threads=1)
if __name__ == "__main__":

    userid_playht, userid_amazon = read_keys()
    key_openai, key_playht, key_amazon = os.environ['KEY_OP'], os.environ['KEY_PLAY'], os.environ['KEY_AMAZON']
    print(sound_provider)
    voice_ids, voice_names = read_voices(sound_provider)


    app.run()