import anki.utils

class ChangeOperation():
    def __init__(self, note):
        self.note = note
        self.newSentence = note['sentence']
        self.newSentenceAudio = note['sentence_audio']

    def hasChanges(self):
        return self.note['sentence'] != self.newSentence or self.note['sentence_audio'] != self.newSentenceAudio

class Syncer():
    def __init__(self, createMedia, notifyUpdate):
        self.createMedia = createMedia
        self.notifyUpdate = notifyUpdate

    def findMatches(self, sentence, expression, entries):
        sentenceMatches = []
        expressionMatches = []

        for audioKey, text in entries.items():
            match = [audioKey.lower(), text]

            if sentence != '' and sentence in text:
                sentenceMatches.append(match)
            elif expression in text:
                expressionMatches.append(match)

        return sentenceMatches + expressionMatches

    def copyAudioFile(self, directory, key):
        target = key + '.ogg'
        file = anki.utils.os.path.join(directory, target)

        try:
            with open(file, 'rb') as handle:
                return self.createMedia(target, handle.read())
        except Exception as e:
            print('error creating media file', e)
            return None

    def updateNote(self, note, match, audioDirectory):
        audioKey, newSentence = match
        audioFile = self.copyAudioFile(audioDirectory, audioKey)

        if audioFile == None:
            return None
            
        return newSentence, '[sound:%s]' % audioFile

    def sync(self, notes, entries, audioDirectory, resolveConflict):
        changeOperations = []

        for note in notes:
            def notify(message):
                self.notifyUpdate(note, message)

            if note == None:
                notify('invalid note')
                continue

            changeOperation = ChangeOperation(note)
            changeOperations.append(changeOperation)

            matches = self.findMatches(note['original_sentence'], note['expression'], entries)
            count = len(matches)

            if count == 0:
                notify('had no matches')
                continue

            if count == 1:
                match = matches[0]
            else:
                match = resolveConflict(note, matches)

                if match == None:
                    notify('skipped while resolving conflict')
                    continue

            updateResult = self.updateNote(note, match, audioDirectory)

            if updateResult == None:
                notify('error creating audio file for %s' % match[0])
                continue

            newSentence, newSentenceAudio = updateResult
            changeOperation.newSentence = newSentence
            changeOperation.newSentenceAudio = newSentenceAudio
            notify('match found, audio: %s - sentence: %s' % (newSentenceAudio, newSentence))
        
        return changeOperations
            


            