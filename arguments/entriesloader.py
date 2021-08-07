from anki.utils import json, os

from ..exceptions import EntriesParseException, InvalidEntriesException

class EntriesLoader():
    def __init__(self):
        self.entries = None

    def escapeText(self, text):
        return text.replace('\\n', '').replace('\n', '').replace('\u3000', ' ')

    def validateEntries(self, entries, audioDirectory):
        validated = []
        validFiles = set(os.listdir(audioDirectory))

        for audioKey, text in entries.items():
            if not isinstance(audioKey, str) or not isinstance(text, str):
                return None

            lowerCaseAudioKey = audioKey.lower()

            if lowerCaseAudioKey not in validFiles:
                print('not a file: %s, skipping' % lowerCaseAudioKey)
                continue
            
            validated.append(Entry(lowerCaseAudioKey, self.escapeText(text), os.path.join(audioDirectory, lowerCaseAudioKey)))

        return validated

    def getEntries(self, file, audioDirectory):
        if self.entries == None:
            entries = None
            
            try:
                with open(file) as data:
                    entries = json.load(data)
            except:
                raise EntriesParseException(file)

            entries = self.validateEntries(entries, audioDirectory)

            if entries == None:
                raise InvalidEntriesException(file)

            self.entries = entries

        return self.entries

class Entry():
    def __init__(self, key, text, path):
        self.key = key
        self.text = text
        self.path = path
