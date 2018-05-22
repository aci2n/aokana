from anki.utils import os

from .changeop import ChangeOperation
from ..arguments.entriesloader import Entry

class Syncer():
    def __init__(self, notifyUpdate, createMedia):
        self.createMedia = createMedia
        self.notifyUpdate = notifyUpdate

    def findMatches(self, sentence, expression, entries):
        sentenceMatches = []
        expressionMatches = []

        for entry in entries:
            if sentence != '' and sentence in entry.text:
                sentenceMatches.append(entry)
            elif expression in entry.text:
                expressionMatches.append(entry)

        return sentenceMatches + expressionMatches

    def copyAudioFile(self, audioKey, audioDirectory):
        if audioKey == '':
            return None

        try:
            return self.createMedia(os.path.join(audioDirectory, audioKey + '.ogg'))
        except Exception as e:
            print('error creating media file', e)
            return None

    def getSentenceAudio(self, audioKey, audioDirectory):
        sentenceAudio = ''
        audioFile = self.copyAudioFile(audioKey, audioDirectory)

        if audioFile != None:
            sentenceAudio = '[sound:%s]' % audioFile

        return sentenceAudio

    def sync(self, args):
        changeOperations = []

        for index, note in enumerate(args.notes):
            def notify(message):
                self.notifyUpdate(note, message, index)

            if note == None:
                notify('invalid note')
                continue

            changeOperation = ChangeOperation(note)
            changeOperations.append(changeOperation)

            matches = self.findMatches(note['original_sentence'], note['expression'], args.entries)
            count = len(matches)

            if count == 0:
                notify('had no matches')
                continue

            matches.append(Entry('', note['original_sentence']))
            match = args.conflictResolver.resolve(note, matches)

            if match == None:
                notify('skipped while resolving conflict')
                continue

            changeOperation.newSentence = match.text
            changeOperation.newSentenceAudio = self.getSentenceAudio(match.key, args.audioDirectory)
            notify('match found, audio: %s - sentence: %s' % (changeOperation.newSentenceAudio, changeOperation.newSentence))
        
        return changeOperations