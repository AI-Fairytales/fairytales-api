#used git https://github.com/shreyashankar/gpt3-sandbox
# @title
import openai
import uuid
import random
import pandas as pd
import re


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
                 engine='davinci',
                 temperature=0.9,
                 max_tokens=1000,
                 presence_penalty=0,
                 best_of=1,
                 n=1,
                 frequency_penalty=0,
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
        self.output_suffix = output_suffix
        self.append_output_prefix_to_query = append_output_prefix_to_query
        self.stop = (output_suffix + input_prefix).strip()
        self.n = n
        self.presence_penalty = presence_penalty
        self.best_of = best_of
        self.frequency_penalty = frequency_penalty
        

    def reset(self):
        self.examples = {}

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
        prompt = self.craft_query(prompt)
        # print(prompt)
        # print("*****************************\n")
        try:
            response = openai.Completion.create(engine=self.get_engine(),
                                                prompt=prompt,
                                                max_tokens=self.get_max_tokens(),
                                                temperature=self.get_temperature(),
                                                top_p=1,
                                                n=self.n,
                                                stream=False,
                                                stop=self.stop)
            return response
        except IOError as error:
            print(error)
            return None

    def get_top_reply(self, prompt):
        """Obtains the best result as returned by the API."""
        response = self.submit_request(prompt)
        max_words = 0
        max_index = 0
        for i in range(self.n):
            temp = words_num(response['choices'][i]['text'])
            # print(temp)
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

    def __init__(self, key, dataset_path, n_answers):
        self.gpt = GPT(engine="text-davinci-002",
                       temperature=0.9,
                       max_tokens=1000,
                       best_of=n_answers,
                       presence_penalty=2,
                       frequency_penalty=0,
                       input_prefix="",
                       input_suffix="\n",
                       output_prefix="",
                       output_suffix="\n\n",
                       n=n_answers)

        self.set_openai_key(key)
        self.n_examples = 1
        self.n_answers = n_answers
        # self.n_cut = 200 #len of example
        # with open(dataset_path, 'w', encoding='utf-8') as r:
        print("*****")
        df = pd.read_csv(dataset_path, sep=';')
        # print(df)
        self.titles = df['title'].values.tolist()
        self.stories = df['story'].values.tolist()
        self.n_tales = len(self.titles)
        # print(df.head())
        # print(self.n_tales)

    def set_openai_key(self, key):
        """Sets OpenAI key."""
        openai.api_key = key

    def set_params(self, nexamples=5, n_cut=200):
        self.n_examples = nexamples
        self.n_cut = n_cut  # len of example

    def postprocess_tale(self, text):
        text = text.replace('\r', '\n')
        text = text.replace('\n\n', '\n')
        result = text
        result = result.replace(".\n", ". \n")
        result = result.replace("!\n", "! \n")
        result = result.replace("?\n", "? \n")
        result = result.replace("\'\n", "\' \n")
        start = 0
        match = re.search("\w\n", result)
        while match:
            match = re.search(r'\w\n', result)
            if match:
                start = match.start()
                print(start)
                result = result[: start + 1] + " " + result[start + 2:]

        return result

    def get_one_tale(self, keyword):
        """generate one tale"""
        self.gpt.reset()  # Marias edition
        for i in range(self.n_examples):
            n = random.randint(0, self.n_tales - 1)
            title = self.titles[n]
            story = self.stories[n]
            result = story
            prompt = f"Write long funny fairy tale for children about " + title

            self.gpt.add_example(Example(prompt, result))

        # keyword = "About A dog catching a ball"
        # ask = f"Write long long long fairy tale of about {keyword} and about the princess who was very capricious"
        ask = f"Write long funny fairy tale for children about {keyword}"
        responce = self.gpt.get_top_reply(ask)
        tale = self.postprocess_tale(responce)
        # sentiment = self.get_sentiment_analyse(tale)
        print("********")
        print(tale)
        return (tale)

    def get_tales_for_json(self, tale_about):

        """generate many tales for json"""
        self.gpt.reset()
        for i in range(self.n_examples):
            n = random.randint(0, self.n_tales - 1)
            title = self.titles[n]
            story = self.stories[n]
            result = story
            self.gpt.add_example(Example(
                'Tell a long fairy tale for preschooler. It should be about ' + title + "\nLong fairy tale for preschooler:",
                # three little pigs and about wolf',
                story))

        prompt = "Tell a long fairy tale for preschooler. It should be about " + tale_about + "." + "\nLong fairy tale for preschooler:"  # and (about one of sword;saber;armor) and and (about one of night;day)"
        output = self.gpt.submit_request(prompt)
        if output == None:
            return [], []
        # print(output)
        tales = []
        prompts = []
        for i in range(self.n_answers):
            # print(len(output.choices[0].text.split()))
            tale = self.postprocess_tale(output.choices[i].text)
            tales.append(tale)
            prompts.append(prompt)
            # prompts.append("123123213")
        return tales, prompts

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