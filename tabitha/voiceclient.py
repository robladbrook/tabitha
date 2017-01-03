""" Tabitha main client class """

import time
from tabitha.objectdict import ObjectDict
from tabitha.sources.pyaudiosource import PyAudioSource
from tabitha.outputs.pyaudiooutput import PyAudioOutput
from tabitha.breakdetectors.vadsilence import VadSilenceDetector
from tabitha.triggers.snowboy import SnowboyTriggerDetector


class VoiceClient(object):
    """ Listens to audio input and execs triggers based vocal commands """

    def __init__(self, config, handle_interrupts=True):
        self.interrupted = False
        self.is_listening = False
        self._source = PyAudioSource(config)
        self._break_detector = VadSilenceDetector(config)
        self._trigger_detector = SnowboyTriggerDetector(config)
        self._output = PyAudioOutput(config)

        self._config = ObjectDict({
            'triggers': {}
            })

        if handle_interrupts:
            import signal
            # capture SIGINT signal, e.g., Ctrl+C
            signal.signal(signal.SIGINT, self._interrupt_handler)

    def listen(self):
        """ starts processing the audio source """
        self._source.start()
        self.is_listening = True

    def _interrupt_handler(self, dummy_signal, dummy_frame):
        self.interrupted = True

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
            if self.interrupted:
                break

            data = self._source.buffer.get_snapshot_data()

            if len(data) == 0:
                time.sleep(self._config.sleep_time)
                continue

            trigger_result = self._trigger_detector.detect(data)

            if not trigger_result:
                continue

            if (trigger_result in self._config.triggers and
                    (not watchfor or trigger_result in watchfor)):
                return self._config.triggers[trigger_result]

    def capture_until_break(self):
        """ blocks and captures audio until a break is detected """

        if not self.is_listening:
            raise ValueError('VoiceClient must be listening to be triggered')

        self._source.buffer.start_capture()
        self._break_detector.reset()

        while self._source.buffer.is_capturing:
            if self.interrupted:
                break

            data = self._source.buffer.get_snapshot_data()

            if len(data) == 0:
                time.sleep(self._config.sleep_time)
                continue

            if self._break_detector.is_break(data):
                self._source.buffer.stop_capture()
                break

        return self._source.buffer.get_capture_data()

    def ask(self, handler, audio_data):
        """ sends the audio data to the handler and waits for response """
        pass

    def play(self, audio_response, stop_on=None):
        """ plays the audio response """
        self._output.play(audio_response)

        # wait for trigger in another thread
        # first one to return (trigger or play)
