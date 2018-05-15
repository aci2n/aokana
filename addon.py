import urllib.request
import urllib.parse
import anki.utils
from .poreader import Reader

class Loader():
    def __init__(self, api):
        self.api = api

    def createParseDialog(self):
        dialog = self.api.qt.QDialog(self.api.window)
        layout = self.api.qt.QGridLayout(dialog)
        dialog.setLayout(layout)

        labelInput = self.api.qt.QLabel('Working directory', dialog)
        textEditInput = self.api.qt.QTextEdit(dialog)
        buttonInput = self.api.qt.QPushButton('Select', dialog)

        buttonParse = self.api.qt.QPushButton('Parse', dialog)

        layout.addWidget(labelInput, 0, 0)
        layout.addWidget(textEditInput, 0, 1)
        layout.addWidget(buttonInput, 0, 2)

        layout.addWidget(buttonParse, 2, 1)

        def buttonInputClicked():
            textEditInput.setText(self.api.qt.QFileDialog.getExistingDirectory(dialog, 'Select the working directory...'))

        buttonInput.clicked.connect(buttonInputClicked)

        def parseButtonClicked():
            directory = textEditInput.toPlainText()

            if directory != '':
                entries = Reader().read(directory)
                file = anki.utils.os.path.join(directory, 'entries.json')

                with open(file, 'w') as out:  
                    anki.utils.json.dump(entries, out)

        buttonParse.clicked.connect(parseButtonClicked)

        return dialog

    def addParseAction(self, dialog):
        action = self.api.qt.QAction('Parse 蒼の彼方', self.api.window)
        action.triggered.connect(lambda: dialog.exec_())
        self.api.addToolsMenuAction(action)

    def load(self):
        self.addParseAction(self.createParseDialog())