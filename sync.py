import anki.utils

class ChangeOperation():
    def __init__(self, note):
        self.note = note
        self.newSentence = note['sentence']
        self.newSentenceAudio = note['sentence_audio']

class Syncer():
    def __init__(self, resolveConflict, createMedia, notifyUpdate):
        self.resolveConflict = resolveConflict
        self.createMedia = createMedia
        self.notifyUpdate = notifyUpdate

    def findMatches(self, sentence, expression, entries):
        sentenceMatches = []
        expressionMatches = []

        for audioKey, text in entries.items():
            key = audioKey.lower()

            if sentence != '' and sentence in text:
                sentenceMatches.append([key, text])
            if expression in text:
                expressionMatches.append([key, text])

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
            
        return [newSentence, '[sound:%s]' % audioFile]

    def sync(self, notes, entries, audioDirectory):
        changeOperations = []

        for note in notes:
            def notify(message):
                self.notifyUpdate(note, message)

            if note == None:
                notify('invalid note id: %d' % id)
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
                match = self.resolveConflict(note, matches)

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
            


            