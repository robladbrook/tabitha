""" provides an audio output using pyaudio """

import io
import wave
import pyaudio
from tabitha.objectdict import ObjectDict


class PyAudioOutput(object):
    """ uses PyAudio to play audio data """

    def __init__(self, config=None):
        config = config or {}
        audio_width = config.get('audio.width', 2)

        self._config = ObjectDict({
            'format': pyaudio.get_format_from_width(audio_width),
            'channels': config.get('audio.channels', 1),
            'sample_rate': config.get('audio.sample_rate', 16000),
            'output_device_index':
                config.get('output.pyaudio.output_device_index', None),
            'frames_per_buffer':
                config.get('output.pyaudio.frames_per_buffer', 1024)})

        self._pyaudio = pyaudio.PyAudio()
        self._audio_stream = None

    def _reset(self):
        self._stop()

        self._audio_stream = self._pyaudio.open(
            input=False,
            output=True,
            format=self._config.format,
            channels=self._config.channels,
            rate=self._config.sample_rate,
            output_device_index=self._config.output_device_index)

    def _stop(self):
        """ stops capturing audio data """

        if self._audio_stream:
            self._audio_stream.close()
            self._audio_stream = None

    def play(self, audio_response):
        """ determines the response type and plays it """

        if not self._pyaudio:
            raise ValueError('Can not play after calling terminate')

        if audio_response.is_stream:
            self.play_stream(audio_response)
        elif audio_response.data:
            self.play_data(audio_response.data)
        else:
            raise ValueError('audio_response is invalid')

    def play_stream(self, stream_response):
        """ plays an audio stream """
        pass

    def play_data(self, audio_data):
        """ plays audio data """

        wav_stream = io.BytesIO(audio_data)
        wav_data = wave.open(wav_stream, 'rb')

        buffer_data = wav_data.readframes(self._config.frames_per_buffer)

        while buffer_data != '':
            self._audio_stream.write(buffer_data)
            buffer_data = wav_data.readframes(self._config.frames_per_buffer)

        wav_data.close()
        wav_stream.close()

    def terminate(self):
        """ terminates pyaudio, releasing resources """

        self._stop()

        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None
