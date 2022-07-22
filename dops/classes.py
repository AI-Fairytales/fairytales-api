#used git https://github.com/shreyashankar/gpt3-sandbox
import openai
import uuid
import random
import pandas as pd

class Example:
    """Stores an input, output pair and formats it to prime the model."""
    def __init__(self, inp, out):
        self.input = inp
        self.output = out
        self.id = uuid.uuid4().hex

    def get_input(self):
        """Returns the input of the example."""
        return self.input

    def get_output(self):
        """Returns the intended output of the example."""
        return self.output

    def get_id(self):
        """Returns the unique ID of the example."""
        return self.id

    def as_dict(self):
        return {
            "input": self.get_input(),
            "output": self.get_output(),
            "id": self.get_id(),
        }
def words_num(text):
        return len(text.split(" "))

class GPT:
    """The main class for a user to interface with the OpenAI API.
    A user can add examples and set parameters of the API request.
    """
    def __init__(self,
                 engine="text-davinci-002",
                 temperature=0.8,
                 max_tokens=1000,
                 input_prefix="input: ",
                 input_suffix="\n",
                 output_prefix="output: ",
                 output_suffix="\n\n",
                 append_output_prefix_to_query=False):
        self.examples = {}
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.input_prefix = input_prefix
        self.input_suffix = input_suffix
        self.output_prefix = output_prefix
        self.n = 3
        self.output_suffix = output_suffix
        self.append_output_prefix_to_query = append_output_prefix_to_query
        self.stop = (output_suffix + input_prefix).strip()

    def add_example(self, ex):
        """Adds an example to the object.
        Example must be an instance of the Example class.
        """
        assert isinstance(ex, Example), "Please create an Example object."
        self.examples[ex.get_id()] = ex

    def delete_example(self, id):
        """Delete example with the specific id."""
        if id in self.examples:
            del self.examples[id]

    def get_example(self, id):
        """Get a single example."""
        return self.examples.get(id, None)

    def get_all_examples(self):
        """Returns all examples as a list of dicts."""
        return {k: v.as_dict() for k, v in self.examples.items()}

    def get_prime_text(self):
        """Formats all examples to prime the model."""
        return "".join(
            [self.format_example(ex) for ex in self.examples.values()])

    def get_engine(self):
        """Returns the engine specified for the API."""
        return self.engine

    def get_temperature(self):
        """Returns the temperature specified for the API."""
        return self.temperature

    def get_max_tokens(self):
        """Returns the max tokens specified for the API."""
        return self.max_tokens

    def craft_query(self, prompt):
        """Creates the query for the API request."""
        q = self.get_prime_text(
        ) + self.input_prefix + prompt + self.input_suffix
        if self.append_output_prefix_to_query:
            q = q + self.output_prefix

        return q

    def submit_request(self, prompt):
        """Calls the OpenAI API with the specified parameters."""
        prompt1 = self.craft_query(prompt)
        print("PROMPT*****************************\n")
        print(prompt1)
        print("*****************************\n")
        response = openai.Completion.create(engine=self.get_engine(),
                                            prompt=prompt1,
                                            max_tokens=self.get_max_tokens(),
                                            temperature=self.get_temperature(),
                                            top_p=1,
                                            n=self.n,
                                            stream=False,
                                            stop=self.stop)
        return response



    def get_top_reply(self, prompt):
        """Obtains the best result as returned by the API."""
        response = self.submit_request(prompt)
        max_words = 0
        max_index = 0
        for i in range(self.n):
            temp = words_num(response['choices'][i]['text'])
            print(temp)
            if temp > max_words:
                max_words = temp
                max_index = i
        return response['choices'][max_index]['text']

    def format_example(self, ex):
        """Formats the input, output pair."""
        return self.input_prefix + ex.get_input(
        ) + self.input_suffix + self.output_prefix + ex.get_output(
        ) + self.output_suffix

    
class FairyTaleGenerator:
    """Stores an input, output pair and formats it to prime the model."""
    def __init__(self, key, dataset_path):
        self.gpt = GPT()
        self.set_openai_key(key)
        self.n_examples = 1
        self.n_cut = 200 #len of example
        #with open(dataset_path, 'w', encoding='utf-8') as r:
        print("*****")
        df = pd.read_csv(dataset_path, sep = ';')
        print(df)
        self.titles = df['title'].values.tolist()
        self.stories = df['story'].values.tolist()
        self.n_tales = len(self.titles)
        #print(df.head())
        #print(self.n_tales)

    def set_openai_key(self, key):
        """Sets OpenAI key."""
        openai.api_key = key   

    def set_params(self, nexamples = 5, n_cut = 200):
        self.n_examples = nexamples
        self.n_cut = n_cut #len of example

     
    def postprocess_tale(self, text):
        def chunk(lst, n):
            for x in range(0, len(lst), n):
                e_c = lst[x : n + x]
                yield e_c

   
        text = text.replace('\n\n', '\n')
        #print(text)
        words_list = text.split(" ")
        #print(words_list)
        parts_list = list(chunk(words_list, 30))
        #print(parts_list)
        parts_str = [" ".join(part) for part in parts_list]
        #print(parts_str)
        result = " ".join(parts_str)
        result = result.replace(".\n", ". \n")
        result = result.replace("!\n", "! \n")
        result = result.replace("?\n", "? \n")
        #result = re.sub("\"[^\s]", "\" ")
        #print(result)
        return result       

    def get_one_tale(self, keyword):
        """generate one tale"""
        self.gpt = GPT() #Marias edition
        for i in range(self.n_examples):
              n = random.randint(0, self.n_tales - 1)
              title = self.titles[n]
              #print(title)
              story = self.stories[n]
              result = story
              #print(len(story.split()))
              #story_list = story.split(" ")
              #result = " ".join(story_list[0 : self.n_cut]).strip()
              prompt = f"Write long long long fairy tale about" + title
              #result = story[0:2000].strip()
              #print(title)
              #print(result)
              
              self.gpt.add_example(Example(prompt, result))

        #keyword = "About A dog catching a ball"      
        #ask = f"Write long long long fairy tale of about {keyword} and about the princess who was very capricious"
        ask = f"Write long long long fairy tale of about {keyword}"
        responce = self.gpt.get_top_reply(ask)
        tale = self.postprocess_tale(responce)
        #sentiment = self.get_sentiment_analyse(tale)
        print("********")
        print(tale)
        return (tale)

    def get_sentiment_analyse(self, tale):
        self.gpt = GPT()
        ask = f"Decide whether a Tale's sentiment is positive, neural or negative\n\n \
                Tale: {tale}\n \
                Sentiment:"
        responce = self.gpt.get_top_reply(ask)
        return responce



    def get_many_tales(self, keywords):  
        tales = []
        for keyword in keywords:
             tales.append(self.get_one_tale(keyword))
        return tales     
            
