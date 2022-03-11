import io
import logging
import os
import signal
import subprocess
import types
from time import sleep

from words import words_dict


class VisionRecog():
    def __init__(self, lang='bg', lang_code='bg-BG'):
        self.lang = lang
        self.lang_code = lang_code
        self.client = vision.ImageAnnotatorClient()

    def get_hints(self):
        hints = words_dict[self.lang]['read_text'] + words_dict[self.lang]['read_logo'] + words_dict[self.lang]['label_detect'] + words_dict[self.lang]['finish_list']
        return hints

    def getImage(self):
        raspistillPID = subprocess.check_output(["pidof", "raspistill"])
        os.kill(int(raspistillPID), signal.SIGUSR1)
        sleep(0.5)
        file_name = "/home/pi/aiyimage.jpg"
        return file_name

    def read_image(self, file_name):
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        return content

    def label_detect(self,content):

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = self.client.label_detection(image=image)
        labels = response.label_annotations
        label_strings = ','.join([label.description for label in labels])
        return label_strings

    def detect_text(self,content):
        image = vision.types.Image(content=content)

        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        texts_content = [text for text in texts]
        texts_strings = texts_content[0].description
        texts_locale = texts_content[0].locale
        return texts_strings, texts_locale

    def detect_logo(self,content):
        image = vision.types.Image(content=content)

        response = self.client.logo_detection(image=image)
        logos = response.logo_annotations
        logo_strings = ','.join([logo.description for logo in logos])
        return logo_strings

    def translate_results(self,text,texts_locale='en'):
        translate_client = translate_v2.Client()
        if texts_locale == self.lang:
            logging.info(f"{words_dict[self.lang]['text_loaded']}\n{text}")
            return text
        else:
            target = self.lang
            translation = translate_client.translate(
            text,
            target_language=target)
            logging.info(f"{words_dict[self.lang]['text_original']}\n{text}")
            translated_results = f"{words_dict[self.lang]['text_resulted']}\n{translation['translatedText']}"
            logging.info(translated_results)
            return translated_results

    def recognition_process(self, text):
        if text in words_dict[self.lang]['read_text']:
            file_name = self.getImage()
            content = self.read_image(file_name)
            texts_results = self.detect_text(content)
            vision_results = texts_results[0]
            texts_locale = texts_results[1]
            results = self.translate_results(vision_results, texts_locale)
        elif text in words_dict[self.lang]['read_logo']:
            file_name = self.getImage()
            content = self.read_image(file_name)
            vision_results = self.detect_logo(content)
            if vision_results:
                results = self.translate_results(vision_results)
            else:
                self.show_say('not_logo')
                results = None
        elif text in words_dict[self.lang]['label_detect']:
            file_name = self.getImage()
            content = self.read_image(file_name)
            vision_results = self.label_detect(content)
            results = self.translate_results(vision_results)
        return results

    def say(self,phrase):
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.types.SynthesisInput(ssml=phrase)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=self.lang_code,
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)
        with open('output.mp3', 'wb') as out:
            out.write(response.audio_content)
        subprocess.run(['mpg321', '-q','-g 20','output.mp3'])

    def show_say(self, phrase, voice=False):
        phrase = words_dict[self.lang][phrase]
        logging.info(phrase)
        if voice:
            self.say(phrase)
