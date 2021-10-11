from anki.utils import os

from .changeop import ChangeOperation
from ..arguments.entriesloader import Entry
from .inflector import Inflector



class Syncer():
    READING_MATCH_CUTOFF = 4

    def __init__(self, notifyUpdate, createMedia):
        self.createMedia = createMedia
        self.notifyUpdate = notifyUpdate
        self.inflector = Inflector()

    def findMatches(self, sentence, expression, reading, entries):
        sentenceMatches = []
        expressionMatches = []
        readingMatches = []
        inflectionMatches = []
        useReading = len(reading) >= Syncer.READING_MATCH_CUTOFF
        inflections = self.inflector.inflect(expression)

        for entry in entries:
            if sentence != '' and sentence in entry.text:
                sentenceMatches.append(entry)
            elif expression in entry.text:
                expressionMatches.append(entry)
            elif useReading and reading in entry.text:
                readingMatches.append(entry)
            elif any(inflection in entry.text for inflection in inflections):
                inflectionMatches.append(entry)

        return sentenceMatches + expressionMatches + readingMatches + inflectionMatches

    def sync(self, args, cancel):
        changeOperations = []
        index = 0
        size = sum(len(notePack['notes']) for notePack in args.notePacks)

        for notePack in args.notePacks:
            notes = notePack['notes']
            mappings = notePack['mappings']
            noteType = notePack['type']
            expressionField = mappings['expressionField']
            sentenceField = mappings['sentenceField']
            readingField = mappings['readingField'] if 'readingField' in mappings else None
            
            for note in notes:
                if cancel():
                    return changeOperations

                index += 1
                expression = note[expressionField]
                sentence = note[sentenceField]
                reading = note[readingField] if readingField != None else ''

                def notify(message):
                    self.notifyUpdate(message, expression, index, size)

                if note == None:
                    notify('invalid note')
                    continue

                changeOperation = ChangeOperation(note, noteType, expression, self.createMedia)
                changeOperations.append(changeOperation)

                matches = self.findMatches(sentence, expression, reading, args.entries)
                count = len(matches)

                if count == 0:
                    notify('had no matches')
                    continue

                match = args.conflictResolver.resolve(expression, matches)

                if match == None:
                    notify('skipped while resolving conflict')
                    continue

                changeOperation.newSentence = match.text
                changeOperation.newSentenceAudio = '[sound:%s]' % match.key
                changeOperation.sentenceAudioFile = match.path

                notify('match found, audio: %s - sentence: %s' % (changeOperation.newSentenceAudio, changeOperation.newSentence))
            
        return changeOperations