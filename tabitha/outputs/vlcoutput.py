""" allows playing of audio media files via the VLC command line """

import os
import subprocess
import threading

_MACOSX_VLC_PATH = '/Applications/VLC.app/Contents/MacOS/VLC'
_VLC_PARAMS = ['-I', 'rc', '--play-and-exit']
_DEVNULL = open(os.devnull, 'w')


class VlcOutput(object):
    """ allows playing of audio media files via the VLC command line """
    def __init__(self, config):
        self.playing = False
        self._current_process = None
        self._play_interrupted = threading.Event()
        self._process_lock = threading.Lock()
        self._on_finish_cb = None

        if 'output.vlc.path' in config:
            self._vlc_path = config['output.vlc.path']
        elif os.path.isfile(_MACOSX_VLC_PATH):
            self._vlc_path = _MACOSX_VLC_PATH
        else:
            raise ValueError('Failed to locate path to VLC, ' +
                             'set output.vlc.path')

    def play(self, audio_url, on_finish_cb=None):
        """ starts playing the audio file and immediately returns """
        if self.playing or self._current_process:
            self.stop()

        vlc_cmd = [self._vlc_path] + _VLC_PARAMS + [audio_url]

        vlc_process = subprocess.Popen(
            vlc_cmd, stdout=_DEVNULL, stderr=_DEVNULL)

        self._current_process = vlc_process
        self._play_interrupted.clear()
        self._on_finish_cb = on_finish_cb
        self.playing = True

        vlc_exit_thread = threading.Thread(
            target=self._wait_for_vlc_exit)
        vlc_exit_thread.start()

    def blocking_play(self, audio_url):
        """ plays the audio file and only returns when complete """
        self.play(audio_url)
        self._current_process.wait()

    def stop(self):
        """ terminates any current vlc process """
        if self.playing and self._current_process:
            with self._process_lock:
                old_process = self._current_process
                self._current_process = None
                self.playing = False
                self._play_interrupted.set()
                old_process.terminate()

    def _wait_for_vlc_exit(self):
        while self.playing:
            return_code = self._current_process.poll()

            if return_code is not None:
                break

            if self._play_interrupted.wait(0.1):
                break

        with self._process_lock:
            self._current_process = None
            self.playing = False

        if self._on_finish_cb:
            self._on_finish_cb()
