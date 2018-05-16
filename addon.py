import anki.utils
import aqt.utils
from .sync import Syncer

class Loader():
    tag = 'aokana'
    ignoreTag = 'aokana_ignore'

    def __init__(self, api):
        self.api = api
        self.syncer = Syncer(self.api.saveMedia, self.printResult)
        self.config = api.getConfig()

    def printResult(self, note, message):
        notification = 'expression: %s: message: %s' % (note['expression'], message)
        print(notification)

    def automaticConflictResolver(self, note, matches):
        return matches[0]

    def getChangeOperations(self, file, audioDirectory, deck, skipTagged, extendedQuery, resolveConflict, dialog):
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

        if skipTagged:
            query += ' -tag:%s' % self.tag
        
        if extendedQuery != '':
            query += ' ' + extendedQuery

        notes = map(self.api.getNoteById, self.api.getNotes(query))

        return self.syncer.sync(notes, entries, audioDirectory, resolveConflict)

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

        return layout, lineEdit.text, lineEdit.setText

    def createFormDialog(self, parent):
        dialog = self.api.qt.QDialog(parent)

        layout = self.api.qt.QFormLayout(dialog)
        layout.setFieldGrowthPolicy(self.api.qt.QFormLayout.ExpandingFieldsGrow)
        dialog.setLayout(layout)

        return dialog, layout

    def validateEntries(self, entries):
        for key, value in entries.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return False

        return True

    def createChangeOperationsTable(self, parent):
        def setChangeOperations(changeOperations):
            table.clear()

            table.setColumnCount(len(headers))
            table.setRowCount(len(changeOperations))
            table.setHorizontalHeaderLabels(headers)

            for i, changeOperation in enumerate(changeOperations):
                background = backgrounds['changed' if changeOperation.hasChanges() else 'unchanged']
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
                    item.setBackground(background)
                    table.setItem(i, j, item)
            
            table.resizeColumnsToContents()

        table = self.api.qt.QTableWidget(parent)
        headers = ['Id', 'Expression', 'Old Audio', 'New Audio', 'Old Sentence', 'New Sentence']
        backgrounds = {
            'changed': self.api.qt.QColor('#f39c12'),
            'unchanged': self.api.qt.QColor('white')
        }

        return table, setChangeOperations

    def createConfirmChangeOperationsDialog(self, parent):
        def updateTable():
            changeOperations = confirmHandler.changeOperations

            if hideUnchangedCheckbox.isChecked():
                changeOperations = list(filter(lambda operation: operation.hasChanges(), changeOperations))
            
            setTableChangeOperations(changeOperations)

        def setChangeOperations(changeOperations):
            confirmHandler.changeOperations = changeOperations
            updateTable()

        def confirmHandler():
            changes = self.confirmChangeOperations(confirmHandler.changeOperations)
            aqt.utils.showInfo('Updated %d notes!' % changes, dialog)
            setChangeOperations([])
            dialog.close()

        dialog = self.api.qt.QDialog(parent)
        
        layout = self.api.qt.QVBoxLayout(dialog)
        dialog.setLayout(layout)

        changeOperationsTable, setTableChangeOperations = self.createChangeOperationsTable(dialog)
        layout.addWidget(changeOperationsTable)

        hideUnchangedCheckbox = self.api.qt.QCheckBox('Hide unchanged', dialog)
        hideUnchangedCheckbox.stateChanged.connect(updateTable)
        layout.addWidget(hideUnchangedCheckbox)

        confirmButton = self.api.qt.QPushButton('Confirm', dialog)
        confirmButton.clicked.connect(confirmHandler)
        layout.addWidget(confirmButton)

        setChangeOperations([])

        return dialog, setChangeOperations

    def getManualConflictResolver(self, parent):
        def getComboBoxItems(matches):
            items = []

            for i, match in enumerate(matches):
                items.append('%d: [%s] - %s' % (i, match[0], match[1]))

            return items

        def resolveConflict(note, matches):
            items = getComboBoxItems(matches)

            choice, success = self.api.qt.QInputDialog.getItem(parent, 'Resolve conflict for "%s"' % note['expression'],
                'Matches', items, editable = False)

            if success:
                index = int(choice.split(':', 1)[0])
                return matches[index]
            else:
                return self.automaticConflictResolver(note, matches)

        return resolveConflict

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
                resolveConflict = manualConflictResolver if getResolveManually() else self.automaticConflictResolver
                changeOperations = self.getChangeOperations(
                    file, audioDirectory, deck, getSkipTagged(), getExtendedQuery(), resolveConflict, dialog)

                if changeOperations != None:
                    setChangeOperations(changeOperations)
                    confirmChangeOperationsDialog.showMaximized()

        def openDialog():
            note = self.api.getCurrentReviewerNote()

            if note != None:
                setExtendedQuery('nid:%d' % note.id)
                skipTaggedCheckbox.setChecked(False)
                resolveManuallyCheckbox.setChecked(True)
            else:
                setExtendedQuery('')
                skipTaggedCheckbox.setChecked(True)
                resolveManuallyCheckbox.setChecked(False)

            dialog.exec_()

        dialog, layout = self.createFormDialog(self.api.window)

        deckBox, getDeck, _ = self.createFormBox(dialog, defaultText = self.config['defaultDeck'])
        layout.addRow('Deck', deckBox)

        entriesFileBox, getEntriesFile, _ = self.createFormBox(dialog, entriesFilePicker,
            defaultText = self.config['defaultEntriesFile'])
        layout.addRow('Entries file', entriesFileBox)

        audioDirectoryBox, getAudioDirectory, _ = self.createFormBox(dialog, audioDirectoryPicker,
            defaultText = self.config['defaultAudioDirectory'])
        layout.addRow('Audio directory', audioDirectoryBox)

        extendedQueryBox, getExtendedQuery, setExtendedQuery = self.createFormBox(dialog)
        layout.addRow('Extended query', extendedQueryBox)

        skipTaggedCheckbox = self.api.qt.QCheckBox(dialog)
        getSkipTagged = skipTaggedCheckbox.isChecked
        layout.addRow('Skip tagged', skipTaggedCheckbox)

        resolveManuallyCheckbox = self.api.qt.QCheckBox(dialog)
        getResolveManually = resolveManuallyCheckbox.isChecked
        layout.addRow('Resolve manually', resolveManuallyCheckbox)

        syncButton = self.api.qt.QPushButton('Sync', dialog)
        syncButton.clicked.connect(syncButtonClicked)
        layout.addRow(syncButton)

        confirmChangeOperationsDialog, setChangeOperations = self.createConfirmChangeOperationsDialog(dialog)

        manualConflictResolver = self.getManualConflictResolver(dialog)
        
        return openDialog

    def addActionWithDialog(self, title, opener, shortcut = None):
        action = self.api.qt.QAction(title, self.api.window)
        action.triggered.connect(opener)
        self.api.addToolsMenuAction(action)

        if shortcut != None:
            action.setShortcut(shortcut)

    def load(self):
        self.api.addToolsMenuSeparator()
        self.addActionWithDialog('Sync 蒼彼方', self.createSyncDialog(), "Ctrl+k")