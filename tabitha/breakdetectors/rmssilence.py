""" RMSSilenceDetector takes a constant stream of audio data
    and waits for the stream to have a run of audio below a threshold """

import logging
import audioop
from tabitha.objectdict import ObjectDict


class RmsSilenceDetector(object):
    """ detects a run of audio silence in an audio data stream """

    def __init__(self, config=None):
        config = config or {}
        drop_start_ms = config.get('break.rms.drop_start_ms', 60)

        self._config = ObjectDict({
            'frame_ms': config.get('break.rms.frame_ms', 30),
            'silence_ms': config.get('break.rms.silence_ms', 200),
            'silence_rms': config.get('break.rms.silence_rms', 0.5),
            'sample_rate': config.get('audio.sample_rate', 16000),
            'audio_width': config.get('audio.width', 2)})

        self._dropped_bytes = 0
        self._silence_run_ms = 0
        self._data = ''

        self._frame_bytes = (self._config.audio_width * self._config.frame_ms *
                             self._config.sample_rate / 1000)
        self._drop_start_bytes = (self._config.audio_width * drop_start_ms *
                                  self._config.sample_rate / 1000)

        logging.debug('__init__ with: ' + config)

    def reset(self):
        """ resets the stream buffer """

        self._silence_run_ms = 0
        self._dropped_bytes = 0
        self._data = ''
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

            rms = audioop.rms(frame, self._config.audio_width)

            if rms > self._config.silence_rms:
                self._silence_run_ms = 0
            else:
                self._silence_run_ms += self._config.frame_ms

            if self._silence_run_ms >= self._config.silence_ms:
                return True

        return False
