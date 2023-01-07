from chatgpt_wrapper import ChatGPT
import replicate
# import pickle
# from pydub import AudioSegment

class Podcast:
    def __init__(self, book_name:str, output_folder:str, topics_number:int ):
        self.book_name = book_name
        self.output_folder = output_folder
        self.topics_number = topics_number
    
    def _make_topic_question(self, topic_n:int):
        topic_question = "can you continue the above conversation with a discussion about the " + str(topic_n) + " topic ? Please make sure that it's coherent with your last response. and please just give me directly the answer."
        return topic_question


    def generate_txt_file(self):
        bot = ChatGPT()
        topics = bot.ask("what are the topics that I should talk about in a podcast about the book " + self.book_name + " ? give me " + str(self.topics_number) + " topics. and please just give me directly the answer")
        intro = bot.ask("can you write me a podcast conversation between 2 hosts talking about the book " + self.book_name + ". first start with an introduction about the above topics. and please just give me directly the answer")
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
        pass


def main():
    podcast = Podcast("The Great Gatsby", "bookast/data/outputs/",8 )
    podcast.generate_txt_file()
   
if __name__ == "__main__":
    main()