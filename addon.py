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
        self.syncer = Syncer(self.api.getNoteById, self.resolveConflict, self.api.saveMedia, self.printResult)

    def printResult(self, result):
        note, message = result
        notification = 'expression: %s: sentence: %s, message: %s' % (note['expression'], note['sentence'], message)
        print(notification)

    def resolveConflict(self, note, matches):
        return matches[0]

    def syncEntries(self, file, audioDirectory, deck, onlyUntagged):
        entries = None

        try:
            with open(file) as data:
                entries = anki.utils.json.load(data)
        except:
            aqt.utils.showInfo('Error parsing entries file (%s)' % file)
            return

        if not self.validateEntries(entries):
            aqt.utils.showInfo('Invalid entries file (%s)' % file)
            return

        query = 'deck:%s' % deck

        if onlyUntagged:
            query += ' -tag:%s' % self.syncer.tag

        notes = self.api.getNotes(query)
        results = self.syncer.sync(notes, entries, audioDirectory)
        aqt.utils.showInfo('Done! Processed %d notes.' % len(results))

    def createFormBox(self, parent, pickerHandler = None, buttonText = 'Select', defaultText = ''):
        layout = self.api.qt.QHBoxLayout()

        lineEdit = self.api.qt.QLineEdit(defaultText, parent)
        layout.addWidget(lineEdit)

        if pickerHandler != None:
            button = self.api.qt.QPushButton(buttonText, parent)
            button.clicked.connect(lambda: lineEdit.setText(pickerHandler()))
            layout.addWidget(button)

        return [layout, lineEdit.text]

    def createDialog(self):
        dialog = self.api.qt.QDialog(self.api.window)

        layout = self.api.qt.QFormLayout(dialog)
        layout.setFieldGrowthPolicy(self.api.qt.QFormLayout.ExpandingFieldsGrow)
        dialog.setLayout(layout)

        return [dialog, layout]

    def writeEntriesFile(self, directory):
        entries = self.reader.read(directory)
        file = anki.utils.os.path.join(directory, 'entries.json')

        try:
            with open(file, 'w') as out: 
                anki.utils.json.dump(entries, out)
                aqt.utils.showInfo('Saved %d entries to: %s' % (len(entries), file))
        except Exception as e:
            print('error saving entries to %s' % file, e)

    def createParseDialog(self):
        def workingDirectoryPicker():
            return self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the working directory...')

        def parseButtonClicked():
            directory = getWorkingDirectory()
            if directory != '':
                self.writeEntriesFile(directory)

        dialog, layout = self.createDialog()

        workingDirectoryBox, getWorkingDirectory = self.createFormBox(dialog, workingDirectoryPicker,
            defaultText = "/Users/alvaro.calace/Documents/aokana/itsusora")
        layout.addRow('Working directory', workingDirectoryBox)

        parseButton = self.api.qt.QPushButton('Parse', dialog)
        parseButton.clicked.connect(parseButtonClicked)
        layout.addRow(parseButton)

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
                self.syncEntries(file, audioDirectory, deck, getOnlyUntagged())

        dialog, layout = self.createDialog()

        deckBox, getDeck = self.createFormBox(dialog, defaultText = 'Vocabulary::Mining')
        layout.addRow('Deck', deckBox)

        entriesFileBox, getEntriesFile = self.createFormBox(dialog, entriesFilePicker,
            defaultText = '/Users/alvaro.calace/Documents/aokana/itsusora/entries.json')
        layout.addRow('Entries file', entriesFileBox)

        audioDirectoryBox, getAudioDirectory = self.createFormBox(dialog, audioDirectoryPicker,
            defaultText = '/Users/alvaro.calace/Documents/aokana/ogg')
        layout.addRow('Audio directory', audioDirectoryBox)

        onlyUntaggedCheckBox = self.api.qt.QCheckBox(dialog)
        onlyUntaggedCheckBox.setChecked(True)
        getOnlyUntagged = onlyUntaggedCheckBox.isChecked
        layout.addRow('Only untagged', onlyUntaggedCheckBox)

        syncButton = self.api.qt.QPushButton('Sync', dialog)
        syncButton.clicked.connect(syncButtonClicked)
        layout.addRow(syncButton)

        return dialog

    def addActionWithDialog(self, title, dialog):
        action = self.api.qt.QAction(title, self.api.window)
        action.triggered.connect(lambda: dialog.exec_())
        self.api.addToolsMenuAction(action)

    def load(self):
        self.api.addToolsMenuSeparator()
        self.addActionWithDialog('Parse 蒼彼方', self.createParseDialog())
        self.addActionWithDialog('Sync 蒼彼方', self.createSyncDialog())