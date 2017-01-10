""" interface to Amazon Alexa Voice Services """

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
import threading
import simpleavs


class AlexaVoiceService(object):
    """ interface to Amazon Alexa Voice Services """

    def __init__(self, config):
        avs_config = {
            'client_id': config['handlers.alexa.client_id'],
            'client_secret': config['handlers.alexa.client_secret'],
            'refresh_token': config['handlers.alexa.refresh_token'],
        }
        self._response_timeout_ms = int(config.get(
            'handlers.alexa.response_timeout_ms', '30000')) / 1000
        self._avs_client = simpleavs.AvsClient(avs_config)
        self._avs_client.speech_synthesizer.speak_event += self._capture_speak
        self._avs_client.connect()
        self._current_dialog_id = None
        self._dialog_response = None
        self._got_dialog_response = threading.Event()

    def _capture_speak(self, speak_directive):
        if speak_directive.dialog_request_id != self._current_dialog_id:
            return

        self._dialog_response = speak_directive
        self._got_dialog_response.set()

    def _speak_to_alexa(self, audio_data, dialog_id):
        self._current_dialog_id = dialog_id

        self._avs_client.speech_recognizer.recognize(
            audio_data=audio_data, profile='NEAR_FIELD',
            dialog_request_id=dialog_id)

        got_response = self._got_dialog_response.wait(
            self._response_timeout_ms)
        self._got_dialog_response.clear()

        if got_response:
            return self._dialog_response

        return None

    def ask(self, audio_data, dummy_context=None):
        """ uses AVS to process the audio and get a response """
        dialog_id = self._avs_client.id_service.get_new_dialog_id()

        return self._speak_to_alexa(audio_data, dialog_id)

    def respond_to(self, audio_data, context):
        """ responds to AVS with audio_data related to previous ask() """
        if 'dialog_id' not in context:
            raise ValueError('respond_to requires a valid dialog_id')

        dialog_id = context['dialog_id']

        return self._speak_to_alexa(audio_data, dialog_id)

    def terminate(self):
        """ release resources """
        self._avs_client.disconnect()
