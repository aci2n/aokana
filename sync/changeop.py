AOKANA_TAG = 'aokana'
AOKANA_IGNORE_TAG = 'aokana_ignore'

class ChangeOperation():
    def __init__(self, note):
        self.note = note
        self.newSentence = note['sentence']
        self.newSentenceAudio = note['sentence_audio']

    def hasFieldChanges(self):
        return self.note['sentence'] != self.newSentence or self.note['sentence_audio'] != self.newSentenceAudio
        
    def applyFieldChanges(self):
        self.note['sentence'] = self.newSentence
        self.note['sentence_audio'] = self.newSentenceAudio

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