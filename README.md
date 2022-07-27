# fairytales-api
Overview of API

There are three endpoints on the API that you will use to get tale's text, tales's sound file and images:

    /tale: get tale, sentiment analyse and analyse for love theme from prompt
    /audio: get audio from tale text
    /images: get images from tale text

The endpoints have been described in detail below.

Endpoints

    Base URL: https://fairytales-api.herokuapp.com/api/v1/

Notes:

    All endpoints are relative to the base URL.
    
Tale

    Endpoint: ./tale?prompt={prompt}&analyse_flag={analyse_flag}

Use this endpoint to generate tale from text prompt and result of tale's analyse.

    Method: GET
    Parameters:
        prompt:  prompt for tale generation
        analyse_flag: whether to analyse the tale

    
    Response (JSON):

    {
      "tale" :  string,
      "sentiment" : string,  
      "love_mood" : boolean,
      "bad_word" : string
    }


Audio

    Endpoint: ./audio?tale={tale}&voice={voice}&sound_provider={sound_provider}

Use this endpoint to generate the sound file from text:
    Parameters:
        tale:  tale to convert to sound
        sound_provider: what TTS provider to use (Play.ht, Amazon)
        voice: what voice of sound provider selected to choose

    Method: GET
    Response (mimetype="audio/x-mpeg-3"):  sound daata

