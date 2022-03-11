import logging
import subprocess

from visionRecog import VisionRecog
from words import words_dict


class Board(object):
    pass


class CloudSpeechClient(object):
    pass


class Led(object):
    pass


def main():
    logging.basicConfig(level=logging.DEBUG)

    vision_recog = VisionRecog('bg', 'bg-BG')

    work = True

    with Board() as board:
        while work:
            board.led.state = Led.PULSE_SLOW
            lang = vision_recog.lang

            vision_recog.show_say('talk_start_button', True)
            hints = vision_recog.get_hints()
            hints_str = "\n".join(hints)
            vision_recog.show_say('command_list')
            logging.info(hints_str)

            vision_recog.show_say('waiting_button')

            client_cloudSpeech = CloudSpeechClient()
            board.button.wait_for_press()

            subprocess.run(['aplay', './button_sound.wav'])

            vision_recog.show_say('waiting_command')

            text = client_cloudSpeech.recognize(language_code=lang, hint_phrases=hints)
            if text is None:
                vision_recog.show_say('talk_sorry', True)
            else:
                results = None
                text = text.lower()
                vision_recog.show_say('your_command')
                logging.info(text)
                if text in hints:
                    if text in words_dict[lang]['finish_list']:
                        vision_recog.show_say('talk_finish', True)
                        work = False
                    else:
                        results= vision_recog.recognition_process(text)
                        vision_recog.say(results)
                else:
                    vision_recog.show_say('talk_again', True)

if __name__ == "__main__":
    main()

