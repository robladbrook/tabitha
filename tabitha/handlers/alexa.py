""" interface to Amazon Alexa Voice Services """


class AlexaVoiceService(object):
    """ interface to Amazon Alexa Voice Services """

    def __init__(self, config=None):
        pass

    def handle(self, audio_data):
        """ uses AVS to process the audio and get a response """
        pass

    def terminate(self):
        """ release resources """
        pass
