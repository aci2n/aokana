
from aqt import qt

class ConfirmTable(qt.QTableWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.headers = ['Id', 'Expression', 'Current Sentence', 'New Sentence', 'New Audio']
        self.backgrounds = {
            'changed': qt.QColor('#f39c12'),
            'unchanged': qt.QColor('#ffffff'),
            'tag': qt.QColor('#55efc4')
        }
    
    def getBackground(self, changeOperation):
        key = 'unchanged'

        if changeOperation.hasFieldChanges():
            key = 'changed'
        elif changeOperation.isUntagged():
            key = 'tag'

        return self.backgrounds[key]

    def setChangeOperations(self, changeOperations):
        self.clear()

        self.setColumnCount(len(self.headers))
        self.setRowCount(len(changeOperations))
        self.setHorizontalHeaderLabels(self.headers)

        for i, changeOperation in enumerate(changeOperations):
            background = self.getBackground(changeOperation)
            fields = enumerate([
                changeOperation.note.id,
                changeOperation.note[changeOperation.noteMappings['expressionField']],
                changeOperation.note[changeOperation.noteMappings['sentenceField']],
                changeOperation.newSentence,
                changeOperation.newSentenceAudio
            ])

            for j, field in fields:
                item = qt.QTableWidgetItem(str(field))
                item.setBackground(background)
                item.setFlags(item.flags() & ~qt.Qt.ItemIsEditable)
                self.setItem(i, j, item)
        
        self.resizeColumnsToContents()

        

    

    