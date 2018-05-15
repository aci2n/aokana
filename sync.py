import anki.utils

class Syncer():
    tag = "aokana3"

    def __init__(self, getNote, resolveConflict, notifyUpdate, createMedia):
        self.getNote = getNote
        self.resolveConflict = resolveConflict
        self.notifyUpdate = notifyUpdate
        self.createMedia = createMedia

    def findMatches(self, sentence, entries):
        matches = []

        for audioKey, text in entries.items():
            if sentence in text:
                matches.append([audioKey, text])

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
        audioKey, sentence = match
        audioFile = self.copyAudioFile(audioDirectory, audioKey)

        if audioFile == None:
            return 'error creating media file for %s' % audioKey
            
        sentenceAudio = '[sound:%s]' % audioFile
        note['sentence'] = sentence
        note['sentence_audio'] = sentenceAudio
        note.addTag(self.tag)
        note.flush()

        return 'updated, sentence_audio: %s - sentence: %s' % (sentenceAudio, sentence)

    def sync(self, notes, entries, audioDirectory):
        results = []

        for id in notes:
            note = self.getNote(id)

            def addResult(message):
                result = [note, message]
                self.notifyUpdate(result)
                results.append(result)

            if note == None:
                addResult('invalid note id: %d' % id)
                continue

            if note['sentence'] == '':
                addResult('does not have a sentence')
                continue
            
            if note.hasTag(self.tag):
                addResult('was already processed')
                continue

            matches = self.findMatches(note['sentence'], entries)
            count = len(matches)

            if count == 0:
                addResult('had no matches')
                continue

            if count == 1:
                match = matches[0]
            else:
                match = self.resolveConflict(note, matches)

                if match == None:
                    addResult('skipped while resolving conflict')
                    continue

            updateResult = self.updateNote(note, match, audioDirectory)
            addResult(updateResult)
        
        return results
            


            