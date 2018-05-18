
from aqt import qt
from .confirmdialog import ConfirmDialog

class SyncDialog(qt.QDialog):
    syncClicked = qt.pyqtSignal()
    confirmClicked = qt.pyqtSignal(list, qt.QDialog)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = qt.QFormLayout()
        self.layout.setFieldGrowthPolicy(qt.QFormLayout.ExpandingFieldsGrow)
        self.setLayout(self.layout)

        self.extendedQueryEdit = qt.QLineEdit()
        self.layout.addRow('Extended query', self.extendedQueryEdit)

        self.skipTaggedCheckBox = qt.QCheckBox()
        self.skipTaggedCheckBox.setChecked(True)
        self.layout.addRow('Skip tagged', self.skipTaggedCheckBox)

        self.resolveManuallyCheckBox = qt.QCheckBox()
        self.layout.addRow('Resolve manually', self.resolveManuallyCheckBox)

        self.syncButton = qt.QPushButton('Sync')
        self.syncButton.clicked.connect(self.syncClicked)
        self.layout.addRow(self.syncButton)

        self.confirmDialog = ConfirmDialog(self)
        self.confirmDialog.confirmClicked.connect(self.onConfirmClicked)

    def exec_(self):
        self.syncButton.setFocus()
        super().exec_()

    def showConfirmDialog(self, changeOperations):
        self.close()
        self.confirmDialog.exec_(changeOperations)

    def onConfirmClicked(self, changeOperations):
        self.confirmClicked.emit(changeOperations, self.confirmDialog)
        self.confirmDialog.close()

    def skipTagged(self):
        return self.skipTaggedCheckBox.isChecked()

    def resolveManually(self):
        return self.resolveManuallyCheckBox.isChecked()

    def extendedQuery(self):
        return self.extendedQueryEdit.text()