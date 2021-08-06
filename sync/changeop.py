AOKANA_TAG = 'aokana'
AOKANA_IGNORE_TAG = 'aokana_ignore'
AOKANA_SENTENCE_FIELD = 'aokana_sentence'
AOKANA_SENTENCE_AUDIO_FIELD = 'aokana_sentence_audio'

class ChangeOperation():
    def __init__(self, note, noteType, expression, createMedia):
        self.note = note
        self.newSentence = note[AOKANA_SENTENCE_FIELD]
        self.newSentenceAudio = note[AOKANA_SENTENCE_AUDIO_FIELD]
        self.noteType = noteType
        self.expression = expression
        self.sentenceAudioFile = None
        self.createMedia = createMedia

    def createSentenceAudioFile(self):
        if self.sentenceAudioFile == None:
            raise Exception('should have a sentence audio file')
        try:
            return self.createMedia(self.sentenceAudioFile)
        except Exception as e:
            print('error creating media file', e)
            raise e

    def hasFieldChanges(self):
        return self.note[AOKANA_SENTENCE_FIELD] != self.newSentence or self.note[AOKANA_SENTENCE_AUDIO_FIELD] != self.newSentenceAudio
        
    def applyFieldChanges(self):
        self.note[AOKANA_SENTENCE_FIELD] = self.newSentence
        self.note[AOKANA_SENTENCE_AUDIO_FIELD] = self.newSentenceAudio

    def isUntagged(self):
        return not self.note.hasTag(AOKANA_TAG)

    def addTag(self):
        self.note.addTag(AOKANA_TAG)

    def hasAnyChanges(self):
        return self.hasFieldChanges() or self.isUntagged()

    def applyAllChanges(self):
        changed = False

        if self.hasFieldChanges():
            self.createSentenceAudioFile() # can throw
            self.applyFieldChanges()
            changed = True

        if self.isUntagged():
            self.addTag()
            changed = True
        
        return changed

    def flush(self):
        self.note.flush()