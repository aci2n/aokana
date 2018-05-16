import urllib.request
import urllib.parse
import anki.utils
import aqt.utils
from .poreader import Reader
from .sync import Syncer

class Loader():
    tag = 'aokana'
    ignoreTag = 'aokana_ignore'

    def __init__(self, api):
        self.api = api
        self.reader = Reader()
        self.syncer = Syncer(self.resolveConflict, self.api.saveMedia, self.printResult)

    def printResult(self, note, message):
        notification = 'expression: %s: message: %s' % (note['expression'], message)
        print(notification)

    def resolveConflict(self, note, matches):
        return matches[0]

    def getChangeOperations(self, file, audioDirectory, deck, onlyUntagged, extendedQuery, dialog):
        entries = None

        if not anki.utils.os.path.isdir(audioDirectory):
            aqt.utils.showInfo('%s is not a directory' % audioDirectory, dialog)
            return None

        try:
            with open(file) as data:
                entries = anki.utils.json.load(data)
        except:
            aqt.utils.showInfo('Error parsing entries file (%s)' % file, dialog)
            return None

        if not self.validateEntries(entries):
            aqt.utils.showInfo('Invalid entries file (%s)' % file, dialog)
            return None

        query = 'deck:%s -tag:%s' % (deck, self.ignoreTag)

        if onlyUntagged:
            query += ' -tag:%s' % self.tag
        
        if extendedQuery != '':
            query += ' ' + extendedQuery

        notes = map(self.api.getNoteById, self.api.getNotes(query))
        return self.syncer.sync(notes, entries, audioDirectory)

    def confirmChangeOperations(self, changeOperations):
        for changeOperation in changeOperations:
            note = changeOperation.note
            note['sentence'] = changeOperation.newSentence
            note['sentence_audio'] = changeOperation.newSentenceAudio
            if not note.hasTag(self.tag): note.addTag(self.tag)
            note.flush()

        self.api.saveCollection()
        return len(changeOperations)

    def createFormBox(self, parent, pickerHandler = None, buttonText = 'Select', defaultText = ''):
        layout = self.api.qt.QHBoxLayout()

        lineEdit = self.api.qt.QLineEdit(defaultText, parent)
        layout.addWidget(lineEdit)

        if pickerHandler != None:
            button = self.api.qt.QPushButton(buttonText, parent)
            button.clicked.connect(lambda: lineEdit.setText(pickerHandler()))
            layout.addWidget(button)

        return [layout, lineEdit.text]

    def createFormDialog(self, parent):
        dialog = self.api.qt.QDialog(parent)

        layout = self.api.qt.QFormLayout(dialog)
        layout.setFieldGrowthPolicy(self.api.qt.QFormLayout.ExpandingFieldsGrow)
        dialog.setLayout(layout)

        return [dialog, layout]

    def writeEntriesFile(self, directory, dialog):
        entries = self.reader.read(directory)
        file = anki.utils.os.path.join(directory, 'entries.json')

        try:
            with open(file, 'w') as out: 
                anki.utils.json.dump(entries, out)
                aqt.utils.showInfo('Saved %d entries to: %s' % (len(entries), file), dialog)
        except Exception as e:
            aqt.utils.showInfo('Error saving entries to %s' % file, e, dialog)

    def createParseDialog(self):
        def workingDirectoryPicker():
            return self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the working directory...')

        def parseButtonClicked():
            directory = getWorkingDirectory()
            if directory != '':
                self.writeEntriesFile(directory, dialog)

        dialog, layout = self.createFormDialog(self.api.window)

        workingDirectoryBox, getWorkingDirectory = self.createFormBox(dialog, workingDirectoryPicker,
            defaultText = 'D:/Code/Bgi_tools/itsusora')
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

    def createChangeOperationsTable(self, parent):
        def updateTable(changeOperations):
            table.clear()

            table.setColumnCount(len(headers))
            table.setRowCount(len(changeOperations))
            table.setHorizontalHeaderLabels(headers)

            for i, changeOperation in enumerate(changeOperations):
                fields = enumerate([
                    changeOperation.note.id,
                    changeOperation.note['expression'],
                    changeOperation.note['sentence_audio'],
                    changeOperation.newSentenceAudio,
                    changeOperation.note['sentence'],
                    changeOperation.newSentence
                ])

                for j, field in fields:
                    item = self.api.qt.QTableWidgetItem(str(field))
                    table.setItem(i, j, item)
            
            table.resizeColumnsToContents()

        table = self.api.qt.QTableWidget(parent)
        headers = ['Id', 'Expression', 'Old Audio', 'New Audio', 'Old Sentence', 'New Sentence']

        return [table, updateTable]

    def createConfirmChangeOperationsDialog(self, parent):
        def setChangeOperations(changeOperations):
            confirmHandler.changeOperations = changeOperations
            updateTable(changeOperations)

        def confirmHandler():
            changes = self.confirmChangeOperations(confirmHandler.changeOperations)
            aqt.utils.showInfo('Updated %d notes!' % changes, dialog)
            setChangeOperations([])
            dialog.close()

        dialog = self.api.qt.QDialog(parent)
        
        layout = self.api.qt.QVBoxLayout(dialog)
        dialog.setLayout(layout)

        changeOperationsTable, updateTable = self.createChangeOperationsTable(dialog)
        layout.addWidget(changeOperationsTable)

        confirmButton = self.api.qt.QPushButton('Confirm', dialog)
        confirmButton.clicked.connect(confirmHandler)
        layout.addWidget(confirmButton)

        setChangeOperations([])

        return [dialog, setChangeOperations]

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
                changeOperations = self.getChangeOperations(file, audioDirectory, deck, getOnlyUntagged(), getExtendedQuery(), dialog)

                if changeOperations != None:
                    setChangeOperations(changeOperations)
                    confirmChangeOperationsDialog.showMaximized()

        dialog, layout = self.createFormDialog(self.api.window)

        deckBox, getDeck = self.createFormBox(dialog, defaultText = 'Vocabulary::Mining')
        layout.addRow('Deck', deckBox)

        entriesFileBox, getEntriesFile = self.createFormBox(dialog, entriesFilePicker,
            defaultText = 'D:/Code/Bgi_tools/itsusora/entries.json')
        layout.addRow('Entries file', entriesFileBox)

        audioDirectoryBox, getAudioDirectory = self.createFormBox(dialog, audioDirectoryPicker,
            defaultText = 'D:/Media/VN Data/aokana/ogg')
        layout.addRow('Audio directory', audioDirectoryBox)

        onlyUntaggedCheckBox = self.api.qt.QCheckBox(dialog)
        onlyUntaggedCheckBox.setChecked(True)
        getOnlyUntagged = onlyUntaggedCheckBox.isChecked
        layout.addRow('Only untagged', onlyUntaggedCheckBox)

        extendedQueryBox, getExtendedQuery = self.createFormBox(dialog)
        layout.addRow('Extended query', extendedQueryBox)

        syncButton = self.api.qt.QPushButton('Sync', dialog)
        syncButton.clicked.connect(syncButtonClicked)
        layout.addRow(syncButton)

        confirmChangeOperationsDialog, setChangeOperations = self.createConfirmChangeOperationsDialog(dialog)

        return dialog

    def addActionWithDialog(self, title, dialog):
        action = self.api.qt.QAction(title, self.api.window)
        action.triggered.connect(lambda: dialog.exec_())
        self.api.addToolsMenuAction(action)

    def load(self):
        self.api.addToolsMenuSeparator()
        #self.addActionWithDialog('Parse 蒼彼方', self.createParseDialog())
        self.addActionWithDialog('Sync 蒼彼方', self.createSyncDialog())