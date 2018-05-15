import urllib.request
import urllib.parse
import anki.utils

class Loader():
    def __init__(self, api):
        self.api = api

    def getUrl(self, kanji, kana):
        return 'https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?' + urllib.parse.urlencode({
            'kanji': kanji,
            'kana': kana
        })

    def shouldSkip(self, data):
        return anki.utils.checksum(data) == '3277fb7a67dd256e0d239e747a69d0f45cd8d1c0'

    def createAudioFile(self, kanji, kana):
        path = ''
        url = self.getUrl(kanji, kana)
        data = urllib.request.urlopen(url).read()

        if self.shouldSkip(data):
            print('no audio found for %s' % kanji)
        else:
            path = 'imported_%s_%s.mp3' % (kanji, kana)
            self.api.saveMedia(path, data)
            print('saved audio file for %s at %s' % (kanji, path))
        
        return path

    def checkNote(self, id):
        note = self.api.getNoteById(id)

        if note['audio'] == '' and note['expression'] != '' and note['reading'] != '':
            path = self.createAudioFile(note['expression'], note['reading'])
            note['audio'] = '[sound:%s]' % path
            note.flush()

        return note

    def showImportDialog(self, dialog):
        notes = self.api.getNotesInDeck('Vocabulary::Mining')

        for note in notes:
            self.checkNote(note)

        self.textEdit.setText(', '.join(map(str, notes)))
        dialog.exec_()

    def createDialog(self):
        dialog = self.api.qt.QDialog(self.api.window)
        layout = self.api.qt.QGridLayout(dialog)
        textEdit = self.api.qt.QTextEdit(dialog)

        layout.addWidget(textEdit)
        dialog.setLayout(layout)
        self.textEdit = textEdit

        return dialog

    def addAction(self, dialog):
        action = self.api.qt.QAction("Import 蒼の彼方", self.api.window)
        action.triggered.connect(lambda: self.showImportDialog(dialog))
        self.api.addToolsMenuAction(action)

    def addImportAction(self):
        self.addAction(self.createDialog())

    def load(self):
        self.addImportAction()