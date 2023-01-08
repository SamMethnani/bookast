from chatgpt_wrapper import ChatGPT
import replicate
from pydub import AudioSegment
import urllib.request
from functools import reduce
from os.path import exists

class Podcast:
    def __init__(self, book_name:str, output_folder:str, topics_number:int ):
        self.book_name = book_name
        self.output_folder = output_folder
        self.topics_number = topics_number
    
    def _make_topic_question(self, topic_n:int):
        topic_question = "can you continue the above conversation with a discussion about the " + str(topic_n) + " topic ? Please make sure that it's coherent with the above conversation and don't do repetitions."
        return topic_question


    def generate_txt_file(self):
        bot = ChatGPT()
        topics = bot.ask("what are the topics that I should talk about in a podcast about the book " + self.book_name + " ? give me " + str(self.topics_number) + " topics.")
        intro = bot.ask("can you write me a podcast conversation between 2 hosts talking about the book " + self.book_name + ". first start with an introduction to the show, the hosts and the book about the above topics, the first host host 1 is Tom and the second host 2 is William. and don't conclude in the end.")
        clean_intro = "\n".join([line for line in intro.split("\n") if line[:4]=="Host"])
        topics_responses=""
        for i in range(1,self.topics_number+1):
            response=  bot.ask(self._make_topic_question(i)) + '\n'
            response= "\n".join([line for line in response.split("\n") if line[:4]=="Host"])
            print("\n".join([line for line in response.split("\n") if line[:4]!="Host"]))
            topics_responses += response+ '\n'

        conclusion = bot.ask("can you conclude the podcast?") 
        clean_conclusion = "\n".join([line for line in conclusion.split("\n") if line[:4]=="Host"])   
        output_file= self.output_folder + self.book_name + " Podcast.txt"
        with open(output_file, "w") as file:
            file.write(clean_intro + '\n'+ topics_responses +'\n'+ clean_conclusion) 
        

    def generate_audio_file(self):
        model = "afiaka87/tortoise-tts"
        version = "e9658de4b325863c4fcdc12d94bb7c9b54cbfe351b7ca1b36860008172b91c71"
        model = replicate.models.get(model)
        version = model.versions.get(version)
        f = open(self.output_folder + self.book_name + " Podcast.txt", 'r')
        text_file = f.read()
        sounds = []
        for ii, line in enumerate(text_file.split("\n")):
            if line.split(" ")[0] == "Host":
                text = line[8:]
                print(text)
                print(line[5])
                voice = "daniel" if line[5]=="1" else "william"
                preset = "standard" # if line[5]=="1" else "fast"
                output_fname = f"bookast/data/outputs/audio_{ii}.mp3"
                if not exists(output_fname):
                    
                    output = version.predict(text= text, voice_a=voice, preset=preset, cvvp_amount=1.0, seed=26031987)
                    
                    urllib.request.urlretrieve(output, output_fname)
            sound = AudioSegment.from_file(output_fname, format="mp3")
            sounds.append(sound)
            

        # sound1, with sound2 appended 
        combined = reduce(lambda x,y:x+y, sounds)

        # export
        combined.export("bookast/bookast/data/outputs/podcast.mp3", format="mp3")


def main():
    podcast = Podcast("The 7 habits of highly effective people", "bookast/bookast/data/outputs/",3 )
    #podcast.generate_txt_file()
    podcast.generate_audio_file()

   
if __name__ == "__main__":
    main()