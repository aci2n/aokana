
from aqt import qt
from .confirmtable import ConfirmTable
from ..sync.changeop import ChangeOperation

class ConfirmDialog(qt.QDialog):
    confirmClicked = qt.pyqtSignal(list)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
        self.resetChangeOperations()

    def initUI(self):
        self.layout = qt.QVBoxLayout()
        self.setLayout(self.layout)

        self.table = ConfirmTable()
        self.layout.addWidget(self.table)

        self.hideUnchangedCheckBox = qt.QCheckBox('Hide unchanged')
        self.hideUnchangedCheckBox.stateChanged.connect(self.updateTable)
        self.layout.addWidget(self.hideUnchangedCheckBox)

        self.confirmButton = qt.QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.onConfirmClicked)
        self.layout.addWidget(self.confirmButton)

    def resetChangeOperations(self):
        self.setChangeOperations([])

    def updateTable(self):
        changeOperations = self.changeOperations

        if self.hideUnchangedCheckBox.isChecked():
            changeOperations = list(filter(ChangeOperation.hasAnyChanges, changeOperations))
        
        self.table.setChangeOperations(changeOperations)

    def setChangeOperations(self, changeOperations):
        self.changeOperations = changeOperations
        self.updateTable()

    def onConfirmClicked(self):
        self.confirmClicked.emit(self.changeOperations)

    def exec_(self, changeOperations):
        self.setChangeOperations(changeOperations)
        self.setWindowState(qt.Qt.WindowMaximized)
        self.confirmButton.setFocus()
        super().exec_()

    def close(self):
        super().close()
        self.resetChangeOperations()