""" Tabitha main client class """

import time
import tempfile
import os
from tabitha.objectdict import ObjectDict
from tabitha.sources.pyaudiosource import PyAudioSource
from tabitha.outputs.vlcoutput import VlcOutput
from tabitha.breakdetectors.vadsilence import VadSilenceDetector
from tabitha.triggers.snowboy import SnowboyTriggerDetector


class VoiceClient(object):
    """ Listens to audio input and execs triggers based vocal commands """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, config=None):
        config = config or {}
        self.is_listening = False
        self._source = PyAudioSource(config)
        self._break_detector = VadSilenceDetector(config)
        self._trigger_detector = SnowboyTriggerDetector(config)
        self._output = VlcOutput(config)
        self._current_context = ObjectDict({
            'capture': None,
            'response': None})

        self._config = ObjectDict({
            'triggers': {},
            'sleep_time': config.get('listen_sleep_time', 0.2)
            })

    def listen(self):
        """ starts processing the audio source """
        self._source.start()
        self.is_listening = True

    def terminate(self):
        """ shuts down the client """
        self.is_listening = False
        self._source.stop()

    def wait_for_hotword(self, watchfor=None):
        """ alias for wait_for_trigger """
        return self.wait_for_trigger(watchfor)

    def wait_for_trigger(self, watchfor=None):
        """ blocks until a trigger is detected """

        if not self.is_listening:
            raise ValueError('VoiceClient must be listening to be triggered')

        watchfor = watchfor or []

        if isinstance(watchfor, basestring):
            watchfor = [watchfor]

        while True:
            if not self.is_listening:
                return None

            data = self._source.buffer.get_snapshot_data()

            if len(data) == 0:
                time.sleep(self._config.sleep_time)
                continue

            trigger_result = self._trigger_detector.detect(data)

            if not trigger_result:
                continue

            # if (trigger_result in self._config.triggers and
            #        (not watchfor or trigger_result in watchfor)):
            #    return self._config.triggers[trigger_result]

            return trigger_result

    def capture_until_break(self):
        """ blocks and captures audio until a break is detected """

        if not self.is_listening:
            raise ValueError('VoiceClient must be listening to be triggered')

        self._source.buffer.start_capture()
        self._break_detector.reset()

        while self._source.buffer.is_capturing:
            if not self.is_listening:
                return None

            data = self._source.buffer.get_snapshot_data()

            if len(data) == 0:
                time.sleep(self._config.sleep_time)
                continue

            if self._break_detector.is_break(data):
                self._source.buffer.stop_capture()
                break

        audio_data = self._source.buffer.get_capture_data()
        self._current_context.capture = audio_data

        return audio_data

    def ask(self, handler, audio_data=None):
        """ sends the audio data to the handler and waits for response """
        if not audio_data:
            audio_data = self._current_context.capture

        response = handler.ask(audio_data)
        self._current_context.response = response

        return response

    def respond_to(self, handler, audio_data=None, response_context=None):
        """ sends the audio data to the handler and waits for response """
        if not audio_data:
            audio_data = self._current_context.capture

        if not response_context:
            response_context = self._current_context.response

        response = handler.respond_to(audio_data, response_context)
        self._current_context.response = response

        return response

    def play(self, audio_response, dummy_stop_on=None):
        """ plays the audio response """

        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)

        with temp_file:
            temp_file.write(audio_response.audio_data)

        self._output.blocking_play(temp_file.name)
        os.remove(temp_file.name)

        # wait for trigger in another thread
        # first one to return (trigger or play)
