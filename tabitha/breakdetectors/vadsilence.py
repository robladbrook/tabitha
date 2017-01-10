""" VadSilenceDetector takes a constant stream of audio data
    and waits for the stream to have a run of vocal silence """

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
import logging
import webrtcvad
from tabitha.objectdict import ObjectDict


class VadSilenceDetector(object):
    """ detects a run of vocal silence in an audio data stream """

    def __init__(self, config=None):
        config = config or {}
        aggressiveness_mode = config.get('break.vad.aggressiveness_mode', 2)
        drop_start_ms = config.get('break.vad.drop_start_ms', 60)

        self._config = ObjectDict({
            'frame_ms': config.get('break.vad.frame_ms', 30),
            'silence_ms': config.get('break.vad.silence_ms', 400),
            'sample_rate': config.get('audio.sample_rate', 16000),
            'audio_width': config.get('audio.width', 2)})

        self._dropped_bytes = 0
        self._silence_run_ms = 0
        self._data = b''

        self._frame_bytes = int(self._config.audio_width *
                                self._config.frame_ms *
                                self._config.sample_rate / 1000)
        self._drop_start_bytes = int(self._config.audio_width *
                                     drop_start_ms *
                                     self._config.sample_rate / 1000)

        self._vad = webrtcvad.Vad(aggressiveness_mode)

        logging.debug('__init__ with: %s', config)

    def reset(self):
        """ resets the stream buffer """

        self._silence_run_ms = 0
        self._dropped_bytes = 0
        self._data = b''
        logging.debug('reset()')

    def is_break(self, data):
        """ appends the audio data and returns True if the stream is silent """

        if not data:
            return False

        if self._dropped_bytes < self._drop_start_bytes:
            self._dropped_bytes += len(data)
            return False

        self._data += data

        while len(self._data) >= self._frame_bytes:
            frame = self._data[:self._frame_bytes]
            self._data = self._data[self._frame_bytes:]

            is_speech = self._vad.is_speech(frame, self._config.sample_rate)

            if is_speech:
                self._silence_run_ms = 0
            else:
                self._silence_run_ms += self._config.frame_ms

            if self._silence_run_ms >= self._config.silence_ms:
                return True

        return False
