from anki.utils import os

from .changeop import ChangeOperation

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

    def copyAudioFile(self, key, audioDirectory):
        target = key + '.ogg'
        file = os.path.join(audioDirectory, target)

        try:
            with open(file, 'rb') as handle:
                return self.createMedia(target, handle.read())
        except Exception as e:
            print('error creating media file', e)
            return None

    def updateNote(self, note, match, audioDirectory):
        audioFile = self.copyAudioFile(match.key, audioDirectory)

        if audioFile == None:
            return None
            
        return UpdateResult(audioFile, match.text)

    def sync(self, args):
        changeOperations = []
        note = None

        def notify(message):
            self.notifyUpdate(note, message)

        for note in args.notes:
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

            if count == 1:
                match = matches[0]
            else:
                match = args.conflictResolver.resolve(note, matches)

                if match == None:
                    notify('skipped while resolving conflict')
                    continue

            updateResult = self.updateNote(note, match, args.audioDirectory)

            if updateResult == None:
                notify('error creating audio file for %s' % match.key)
                continue

            changeOperation.newSentence = updateResult.sentence
            changeOperation.newSentenceAudio = updateResult.sentenceAudio
            notify('match found, audio: %s - sentence: %s' % (updateResult.sentenceAudio, updateResult.sentence))
        
        return changeOperations
            
class UpdateResult():
    def __init__(self, audioFile, sentence):
        self.sentenceAudio = '[sound:%s]' % audioFile
        self.sentence = sentence