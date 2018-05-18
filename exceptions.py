class AokanaException(Exception):
    def __init__(self, message):
        self.message = message

    def getMessage(self):
        return self.message

class SyncArgumentsException(AokanaException):
    pass
        
class EntriesException(SyncArgumentsException):
    pass

class InvalidEntriesException(EntriesException):
    def __init__(self, file):
        super().__init__('Invalid entries file (%s)' % file)

class EntriesParseException(EntriesException):
    def __init__(self, file):
        super().__init__('Error parsing entries file (%s)' % file)

class ConfigException(SyncArgumentsException):
    pass

class MissingConfigException(ConfigException):
    def __init__(self):
        super().__init__('One or more configuration parameters are missing.')

class InexistentAudioDirectoryException(ConfigException):
    def __init__(self, directory):
        super().__init__('Inexistent audio directory: %s' % directory)

class InexistentEntriesFileException(ConfigException):
    def __init__(self, file):
        super().__init__('Inexistent entries file: %s' % file)