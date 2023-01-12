import urllib.request
from functools import reduce
from os.path import exists
from pathlib import Path

import replicate
import typer
from chatgpt_wrapper import ChatGPT
from pydub import AudioSegment
from config import config


class Podcast:
    def __init__(self, book_name: str, output_dir: Path, topics_number: int):
        self.book_name = book_name
        self.output_dir = output_dir
        self.topics_number = topics_number

    def _make_topic_question(self, topic_n: int) -> str:
        """Make a question to ask the bot about a topic.

        Arguments:
            topic_n -- Topic number

        Returns:
            Topic question as str
        """
        topic_question = "can you continue the above conversation with a discussion about the " + \
            str(topic_n) + " topic ? Please make sure that it's coherent with the above conversation and don't repeat words or ideas."
        return topic_question

    def generate_txt_file(self):
        """Generate a txt file with the podcast conversation. File is saved in the output folder.
        Args:
            self.book_name (str): The name of the book.
            self.topics_number (int): The number of topics to discuss.
            self.output_dir (str): The folder to save the output file.
        Returns:
            None. Writes a txt file in the output folder under the file name: book_name Podcast.txt
        """
        bot = ChatGPT()
        topics = bot.ask("what are the topics that I should talk about in a podcast about the book " +
                         self.book_name + " ? give me " + str(self.topics_number) + " topics.")
        intro = bot.ask("can you write me a conversation between 2 hosts of a book podcast. write me an introduction to a the show, and the book " + self.book_name +
                        ".the topics they're going to talk about are the above topics. Both hosts are men. and don't conclude in the end.")
        clean_intro = "\n".join([line for line in intro.split("\n") if line[:4] == "Host"])
        topics_responses = ""
        for i in range(1, self.topics_number+1):
            response = bot.ask(self._make_topic_question(i)) + '\n'
            response = "\n".join([line for line in response.split("\n") if line[:4] == "Host"])
            print("\n".join([line for line in response.split("\n") if line[:4] != "Host"]))
            topics_responses += response + '\n'

        conclusion = bot.ask("can you conclude the podcast?")
        clean_conclusion = "\n".join([line for line in conclusion.split("\n") if line[:4] == "Host"])
        (self.output_dir / self.book_name).mkdir(parents=True, exist_ok=True)
        print((self.output_dir / self.book_name))
        output_file = self.output_dir / self.book_name / "podcast.txt"
        with output_file.open("w") as file:
            file.write(clean_intro + '\n' + topics_responses + '\n' + clean_conclusion)

    def _normalize_audio_lufs(self, sound, target_lufs=-23.0):
        loudness_before = sound.dBFS
        sound = sound.apply_gain(target_lufs - loudness_before)
        return sound

    def generate_audio_file(self):
        """Generate an audio file with the podcast conversation. File is saved in the output folder.
        Args:
            self.book_name (str): The name of the book.
            self.output_dir (str): The folder to save the output file.
        Returns:
            None. Writes an audio file in the output folder under the file name: self.output_dir / self.book_name + "_podcast.mp3"
        """
        model = "afiaka87/tortoise-tts"
        version = "e9658de4b325863c4fcdc12d94bb7c9b54cbfe351b7ca1b36860008172b91c71"
        client = replicate.Client(api_token=config.replicate_api_key)
        model = client.models.get(model)
        version = model.versions.get(version)

        sounds = []
        with (self.output_dir / self.book_name / "podcast.txt").open("r") as f:
            for ii, line in enumerate(f):
                if line.split(" ")[0] == "Host":
                    text = line[8:]
                    print(text)
                    print(line[5])
                    voice = "daniel" if line[5] == "1" else "william"
                    preset = "standard"
                    output_fname = self.output_dir / self.book_name / f"audio_{ii}.mp3"
                    if not exists(output_fname):

                        output = version.predict(text=text, voice_a=voice, 
                                                 reset=preset, cvvp_amount=1.0, seed=26031987)

                        urllib.request.urlretrieve(output, output_fname)
                    sound = self._normalize_audio_lufs(AudioSegment.from_file(output_fname, format="mp3"))
                    sounds.append(sound)

        # sound1, with sound2 appended
        combined = reduce(lambda x, y: x+y, sounds)

        # export
        combined.export(str(self.output_dir / self.book_name / "podcast.mp3"), format="mp3")


def main(book_name: str = typer.Option("The 7 habits of highly effective people", help="The name of the book to discuss in the podcast"),
         topics_number: int = typer.Option(3, help="The number of topics to discuss in the podcast"),
         output_dir: Path = typer.Option(None, help="The output directory for the generated podcast")):
    """Generate a podcast about a book."""

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / 'data' / 'outputs'

    podcast = Podcast(book_name, output_dir, topics_number)
    podcast.generate_txt_file()
    podcast.generate_audio_file()


if __name__ == "__main__":
    typer.run(main)
