import urllib.request
import urllib.parse
import anki.utils
import aqt.utils
from .poreader import Reader

class Loader():
    def __init__(self, api):
        self.api = api

    def syncEntries(self, entries):
        return

    def createDialog(self, labelInputTitle, buttonRunTitle, filePicker, buttonRunClicked):
        dialog = self.api.qt.QDialog(self.api.window)
        layout = self.api.qt.QGridLayout(dialog)
        dialog.setLayout(layout)

        labelInput = self.api.qt.QLabel(labelInputTitle, dialog)
        textEditInput = self.api.qt.QTextEdit(dialog)
        buttonInput = self.api.qt.QPushButton('Select', dialog)

        buttonRun = self.api.qt.QPushButton(buttonRunTitle, dialog)

        layout.addWidget(labelInput, 0, 0)
        layout.addWidget(textEditInput, 0, 1)
        layout.addWidget(buttonInput, 0, 2)

        layout.addWidget(buttonRun, 2, 1)

        def buttonInputClicked():
            textEditInput.setText(filePicker(dialog))

        buttonInput.clicked.connect(buttonInputClicked)
        buttonRun.clicked.connect(lambda: buttonRunClicked(textEditInput.toPlainText()))

        return dialog

    def createParseDialog(self):
        def filePicker(dialog):
            return self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the working directory...')

        def parseButtonClicked(directory):
            if directory != '':
                entries = Reader().read(directory)
                file = anki.utils.os.path.join(directory, 'entries.json')

                with open(file, 'w') as out:  
                    anki.utils.json.dump(entries, out)

        return self.createDialog('Working directory', 'Parse', filePicker, parseButtonClicked)

    def createSyncDialog(self):
        def filePicker(dialog):
            file, _ = self.api.qt.QFileDialog.getOpenFileName(dialog, 'Select the entries file...')
            return file

        def syncButtonClicked(file):
            try:
                with open(file) as data:
                    entries = anki.utils.json.load(data)
                    self.syncEntries(entries)
            except:
                aqt.utils.showInfo('Invalid file (%s)' % file)

        return self.createDialog('Entries file', 'Sync', filePicker, syncButtonClicked)

    def addActionWithDialog(self, title, dialog):
        action = self.api.qt.QAction(title, self.api.window)
        action.triggered.connect(lambda: dialog.exec_())
        self.api.addToolsMenuAction(action)

    def load(self):
        self.api.addToolsMenuSeparator()
        self.addActionWithDialog('Parse 蒼の彼方', self.createParseDialog())
        self.addActionWithDialog('Sync 蒼の彼方', self.createSyncDialog())