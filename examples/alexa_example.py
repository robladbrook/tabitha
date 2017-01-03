""" sample to demonstrate Tabitha running as Alexa """

import yaml
from tabitha.voiceclient import VoiceClient
from tabitha.handlers.alexa import AlexaVoiceService


def main():
    """ runs as Amazon Alexa """

    with open("alexa_example_config.yml", 'r') as ymlfile:
        config = yaml.load(ymlfile)

    alexa = VoiceClient(config)
    avs = AlexaVoiceService(config)

    while alexa.is_listening:
        alexa.wait_for_hotword('alexa')
        audio_data = alexa.capture_until_break()
        avs_response = alexa.ask(avs, audio_data)
        alexa.play(avs_response, stop_on=['alexa', 'stop'])

if __name__ == '__main__':
    main()
