from app import app
from dops.functions import *
from app import *



if __name__ == "__main__":

    userid_playht, userid_amazon = read_keys()
    key_openai, key_playht, key_amazon = os.environ['KEY_OP'], os.environ['KEY_PLAY'], os.environ['KEY_AMAZON']
    print(sound_provider)
    voice_ids, voice_names = read_voices(sound_provider)


    app.run()
