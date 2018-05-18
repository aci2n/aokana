from anki.utils import os

from ..exceptions import InexistentAudioDirectoryException, InexistentEntriesFileException, MissingConfigException

class ConfigValidator():
    def __init__(self, config):
        self.config = config

    def validate(self):
        entriesFile = self.config['entriesFile']
        audioDirectory = self.config['audioDirectory']
        noteType = self.config['noteType']

        if entriesFile == '' or audioDirectory == '' or noteType == '':
            raise MissingConfigException()

        if not os.path.isdir(audioDirectory):
            raise InexistentAudioDirectoryException(audioDirectory)

        if not os.path.exists(entriesFile):
            raise InexistentEntriesFileException(entriesFile)

        return ValidatedConfig(entriesFile, audioDirectory, noteType)

class ValidatedConfig():
    def __init__(self, entriesFile, audioDirectory, noteType):
        self.entriesFile = entriesFile
        self.audioDirectory = audioDirectory
        self.noteType = noteType
