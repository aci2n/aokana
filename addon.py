import urllib.request
import urllib.parse
import anki.utils
import aqt.utils
from .poreader import Reader
from .sync import Syncer

class Loader():
    def __init__(self, api):
        self.api = api
        self.reader = Reader()
        self.syncer = Syncer(self.api.getNoteById, self.resolveConflict, self.notifyUpdate, self.api.saveMedia)

    def resolveConflict(self, note, matches):
        return matches[0]

    def notifyUpdate(self, result):
        return None

    def syncEntries(self, file, audioDirectory, deck):
        entries = None

        try:
            with open(file) as data:
                entries = anki.utils.json.load(data)
        except:
            aqt.utils.showInfo('Error parsing entries file (%s)' % file)
            return

        if self.validateEntries(entries):
            self.syncEntries(entries, audioDirectory, deck)
        else:
            aqt.utils.showInfo('Invalid entries file (%s)' % file)
            return

        notes = self.api.getNotesInDeck(deck)

        return self.syncer.sync(notes, entries, audioDirectory)

    def createPickerBox(self, labelText, picker, parent):
        box = self.api.qt.QWidget(parent)
        layout = self.api.qt.QHBoxLayout(box)
        label = self.api.qt.QLabel(labelText, box)
        textEdit = self.api.qt.QTextEdit(box)

        layout.addWidget(label)
        layout.addWidget(textEdit)
        box.setLayout(layout)

        if picker != None:
            button = self.api.qt.QPushButton('Select', box)
            button.clicked.connect(lambda: textEdit.setText(picker()))
            layout.addWidget(button)

        def getText():
            return textEdit.toPlainText()

        return [box, getText]

    def createDialog(self):
        dialog = self.api.qt.QDialog(self.api.window)
        layout = self.api.qt.QVBoxLayout(dialog)

        dialog.setLayout(layout)

        return [dialog, layout]

    def writeEntriesFile(self, directory):
        entries = self.reader.read(directory)
        file = anki.utils.os.path.join(directory, 'entries.json')

        with open(file, 'w') as out:  
            anki.utils.json.dump(entries, out)
            aqt.utils.showInfo('Saved entries to: %s' % file)

        return file

    def createParseDialog(self):
        def filePicker():
            return self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the working directory...')

        def parseButtonClicked():
            directory = getWorkingDirectory()

            if directory != '':
                self.writeEntriesFile(directory)

        dialog, layout = self.createDialog()
        workingDirectoryBox, getWorkingDirectory = self.createPickerBox('Working directory', filePicker, dialog)
        parseButton = self.api.qt.QPushButton('Parse', dialog)

        parseButton.clicked.connect(parseButtonClicked)

        layout.addWidget(workingDirectoryBox)
        layout.addWidget(parseButton)

        return dialog

    def validateEntries(self, entries):
        for key, value in entries.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return False

        return True

    def createSyncDialog(self):
        def entriesFilePicker():
            file, _ = self.api.qt.QFileDialog.getOpenFileName(dialog, 'Select the entries file...')
            return file

        def audioDirectoryPicker():
            return self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the audio files directory...')

        def syncButtonClicked():
            file = getEntriesFile()
            audioDirectory = getAudioDirectory()
            deck = getDeck()

            if file != '' and audioDirectory != '' and deck != '':
                self.syncEntries(file, audioDirectory, deck)

        dialog, layout = self.createDialog()
        deckBox, getDeck = self.createPickerBox('Deck name', None, dialog)
        entriesFileBox, getEntriesFile = self.createPickerBox('Entries file', entriesFilePicker, dialog)
        audioDirectoryBox, getAudioDirectory = self.createPickerBox('Audio directory', audioDirectoryPicker, dialog)
        syncButton = self.api.qt.QPushButton('Sync', dialog)

        syncButton.clicked.connect(syncButtonClicked)

        layout.addWidget(deckBox)
        layout.addWidget(entriesFileBox)
        layout.addWidget(audioDirectoryBox)
        layout.addWidget(syncButton)

        return dialog

    def addActionWithDialog(self, title, dialog):
        action = self.api.qt.QAction(title, self.api.window)
        action.triggered.connect(lambda: dialog.exec_())
        self.api.addToolsMenuAction(action)

    def load(self):
        self.api.addToolsMenuSeparator()
        self.addActionWithDialog('Parse 蒼の彼方', self.createParseDialog())
        self.addActionWithDialog('Sync 蒼の彼方', self.createSyncDialog())