from anki.utils import json

from ..exceptions import EntriesParseException, InvalidEntriesException

class EntriesLoader():
    def __init__(self):
        self.entries = None

    def escapeText(self, text):
        return text.replace('\\n', '')

    def validateEntries(self, entries):
        validated = []

        for audioKey, text in entries.items():
            if isinstance(audioKey, str) and isinstance(text, str):
                validated.append(Entry(audioKey.lower(), self.escapeText(text)))
            else:
                return None

        return validated

    def getEntries(self, file):
        if self.entries == None:
            entries = None
            
            try:
                with open(file) as data:
                    entries = json.load(data)
            except:
                raise EntriesParseException(file)

            entries = self.validateEntries(entries)

            if entries == None:
                raise InvalidEntriesException(file)

            self.entries = entries

        return self.entries

class Entry():
    def __init__(self, key, text):
        self.key = key
        self.text = text
