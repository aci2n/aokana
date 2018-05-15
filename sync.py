import anki.utils

class ChangeOperation():
    def __init__(self, note, newSentence, newSentenceAudio):
        self.note = note
        self.newSentence = newSentence
        self.newSentenceAudio = newSentenceAudio

class Syncer():
    def __init__(self, resolveConflict, createMedia, notifyUpdate):
        self.resolveConflict = resolveConflict
        self.createMedia = createMedia
        self.notifyUpdate = notifyUpdate

    def findMatches(self, sentence, entries):
        matches = []

        for audioKey, text in entries.items():
            if sentence in text:
                matches.append([audioKey.lower(), text])

        return matches

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
            
        return ChangeOperation(note, newSentence, '[sound:%s]' % audioFile)

    def sync(self, notes, entries, audioDirectory):
        changeOperations = []

        for note in notes:
            def notify(message):
                self.notifyUpdate(note, message)

            if note == None:
                notify('invalid note id: %d' % id)
                continue

            if note['sentence'] == '':
                notify('does not have a sentence')
                continue
            
            matches = self.findMatches(note['sentence'], entries)
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

            changeOperation = self.updateNote(note, match, audioDirectory)

            if changeOperation == None:
                notify('error creating audio file for %s' % match[0])
                continue

            changeOperations.append(changeOperation)
            notify('match found, audio: %s - sentence: %s' % (changeOperation.newSentenceAudio, changeOperation.newSentence))
        
        return changeOperations
            


            