from aqt import mw, qt

class Anki():
    def __init__(self):
        self.window = mw
        self.qt = qt

    def addToolsMenuAction(self, action):
        return self.window.form.menuTools.addAction(action)
    
    def getNotesInDeck(self, deck):
        return self.window.col.findNotes('deck:%s' % deck)

    def getNoteById(self, id):
        return self.window.col.getNote(id)

    def saveMedia(self, path, data):
        return self.window.col.media.writeData(path, data)