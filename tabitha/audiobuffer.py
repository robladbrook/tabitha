""" AudioBuffer holds audio data to be post processed """

from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
import collections


class AudioBuffer(object):
    """ AudioBuffer holds audio data to be post processed """

    def __init__(self, config=None):
        config = config or {}
        snapshot_ms = config.get('audio.buffer.snapshot_ms', 120)
        max_capture_ms = config.get('audio.buffer.max_capture_ms', 6000)
        sample_rate = config.get('audio.sample_rate', 16000)
        audio_width = config.get('audio.width', 2)

        capture_buffer_size = None
        snapshot_buffer_size = audio_width * snapshot_ms * sample_rate / 1000

        if max_capture_ms:
            capture_buffer_size = (audio_width * max_capture_ms *
                                   sample_rate / 1000)

        self.is_capturing = False
        self._snapshot_buffer = collections.deque(maxlen=snapshot_buffer_size)
        self._capture_buffer = collections.deque(maxlen=capture_buffer_size)

    def extend(self, data):
        """ add new audio data to the buffer """

        self._snapshot_buffer.extend(data)

        if self.is_capturing:
            self._capture_buffer.extend(data)
            self._check_if_capture_complete()

    def get_snapshot_data(self):
        """ returns a small snapshot of the most recent audio data """

        tmp = bytes(bytearray(self._snapshot_buffer))
        self._snapshot_buffer.clear()
        return tmp

    def start_capture(self):
        """ starts capturing audio data into a larger capture buffer """

        self._capture_buffer.clear()
        self.is_capturing = True

    def stop_capture(self):
        """ stops capturing audio into the capture buffer """

        self.is_capturing = False

    def get_capture_data(self):
        """ returns the captured audio data """

        return bytes(bytearray(self._capture_buffer))

    def _check_if_capture_complete(self):
        if len(self._capture_buffer) == self._capture_buffer.maxlen:
            self.is_capturing = False
