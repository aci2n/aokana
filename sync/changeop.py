AOKANA_TAG = 'aokana'
AOKANA_IGNORE_TAG = 'aokana_ignore'
AOKANA_SENTENCE_FIELD = 'aokana_sentence'
AOKANA_SENTENCE_AUDIO_FIELD = 'aokana_sentence_audio'

class ChangeOperation():
    def __init__(self, note, noteMappings):
        self.note = note
        self.newSentence = note[AOKANA_SENTENCE_FIELD]
        self.newSentenceAudio = note[AOKANA_SENTENCE_AUDIO_FIELD]
        self.noteMappings = noteMappings

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
            self.applyFieldChanges()
            changed = True

        if self.isUntagged():
            self.addTag()
            changed = True
        
        return changed

    def flush(self):
        self.note.flush()