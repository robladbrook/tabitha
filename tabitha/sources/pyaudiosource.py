""" provides a source of audio data using pyaudio """

import pyaudio
from tabitha.objectdict import ObjectDict


class PyAudioSource(object):
    """ uses PyAudio to capture audio data """

    def __init__(self, config=None, audio_buffer=None):
        config = config or {}

        if not audio_buffer:
            from tabitha.audiobuffer import AudioBuffer
            audio_buffer = AudioBuffer()

        audio_width = config.get('audio.width', 2)

        self._config = ObjectDict({
            'format': pyaudio.get_format_from_width(audio_width),
            'channels': config.get('audio.channels', 1),
            'rate': config.get('audio.sample_rate', 16000),
            'frames_per_buffer': config.get('source.pyaudio.frames_per_buffer',
                                            1024),
            'input_device_index':
                config.get('source.pyaudio.input_device_index', None)})

        self._pyaudio = pyaudio.PyAudio()
        self._audio_stream = None
        self.buffer = audio_buffer

    def _stream_callback(self, in_data, dummy_frame_count,
                         dummy_time_info, dummy_status):
        self.buffer.extend(in_data)
        play_data = chr(0) * len(in_data)
        return play_data, pyaudio.paContinue

    def start(self):
        """ starts filling the audio buffer with data """

        if not self._pyaudio:
            raise ValueError('Can not start source after calling terminate')

        self._audio_stream = self._pyaudio.open(
            input=True,
            output=False,
            format=self._config.format,
            channels=self._config.channels,
            rate=self._config.rate,
            frames_per_buffer=self._config.frames_per_buffer,
            input_device_index=self._config.input_device_index,
            stream_callback=self._stream_callback)

    def stop(self):
        """ stops capturing audio data """

        if self._audio_stream:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self._audio_stream = None

    def terminate(self):
        """ terminates pyaudio, releasing resources """

        self.stop()

        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None
