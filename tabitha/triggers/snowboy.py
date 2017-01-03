""" uses Snowboy to detect hotword triggers """

import os.path
from tabitha.triggers.snowboydetect import SnowboyDetect


class SnowboyTriggerDetector(object):
    """ uses Snowboy to detect hotword triggers """

    def __init__(self, config=None):
        config = config or {}

        top_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(top_dir, '../../resources/snowboy/')
        resource_file = os.path.join(resources_dir, 'common.res')
        model_file = os.path.join(resources_dir, 'tabitha.pmdl')

        resource = config.get('trigger.snowboy.commonres', resource_file)
        model = config.get('trigger.snowboy.model', model_file)
        audio_gain = config.get('trigger.snowboy.audio_gain', 1)
        sensitivity = config.get('trigger.snowboy.sensitivity', 0.5)

        self._detector = SnowboyDetect(
            resource_filename=resource.encode(), model_str=model.encode())
        self._detector.SetAudioGain(audio_gain)
        self._detector.SetSensitivity(sensitivity)

        self.validate_audio_config(config)

    def validate_audio_config(self, config):
        """ validates a given audio config against snowboy settings """

        config_sample_rate = config.get('audio.sample_rate', 16000)
        config_channels = config.get('audio.channels', 1)
        config_bits_per_sample = config.get('audio.bits_per_sample', 8)

        snowboy_sample_rate = self._detector.SampleRate()
        snowboy_channels = self._detector.NumChannels()
        snowboy_bits_per_sample = self._detector.BitsPerSample()

        if config_sample_rate != snowboy_sample_rate:
            raise ValueError(('Snowboy expected sample_rate to be %s ' +
                              'but was configured with %s') %
                             (snowboy_sample_rate, config_sample_rate))

        if config_channels != snowboy_channels:
            raise ValueError(('Snowboy expected channels to be %s ' +
                              'but was configured with %s') %
                             (snowboy_channels, config_channels))

        if config_bits_per_sample != snowboy_bits_per_sample:
            raise ValueError(('Snowboy expected snowboy_bits_per_sample to ' +
                              'be %s but was configured with %s') %
                             (snowboy_bits_per_sample, config_bits_per_sample))

    def detect(self, data):
        """ returns the 1-based index of the word detected """

        hotword_index = self._detector.RunDetection(data)

        if hotword_index > 0:
            return hotword_index
        else:
            return None
