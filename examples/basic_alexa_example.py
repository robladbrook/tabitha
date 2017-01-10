""" sample to demonstrate Tabitha running as Alexa """

from __future__ import print_function
import os
import io
import sys
import signal
import yaml

# import logging
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# pylint: disable=wrong-import-position
import tabitha
from tabitha.handlers.alexa import AlexaVoiceService

_EXAMPLES_DIR = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join(_EXAMPLES_DIR, 'client_config.yml')


def main():
    """ runs as a basic version of Amazon Echo """

    with io.open(_CONFIG_PATH, 'r') as cfile:
        config = yaml.load(cfile)

    echo = tabitha.VoiceClient()
    avs = AlexaVoiceService(config)

    def _terminate(dummy1, dummy2):
        print('Quitting...')
        avs.terminate()
        echo.terminate()
        exit()

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, _terminate)

    echo.listen()
    print('Echo has started, press Ctrl+C to quit')

    while echo.is_listening:
        print('Listening for "Alexa"...')
        hotword = echo.wait_for_hotword('alexa')

        if not hotword:
            return

        print('Caught hotword: alexa')
        initial_query = True
        expects_more_dialog = False

        while initial_query or expects_more_dialog:
            capture = echo.capture_until_break()

            if not capture:
                return

            print('Received request, sending to AVS')

            if initial_query:
                avs_response = echo.ask(avs)
                initial_query = False
            else:
                avs_response = echo.respond_to(avs)

            if avs_response:
                print('Playing AVS response')
                echo.play(avs_response)  # , stop_on=['alexa', 'stop'])
            #  expects_more_dialog = avs_response.expects_more_dialog


if __name__ == '__main__':
    main()
