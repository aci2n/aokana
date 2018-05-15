from aqt import mw, qt

class Anki():
    def __init__(self):
        self.window = mw
        self.qt = qt

    def addToolsMenuAction(self, action):
        return self.window.form.menuTools.addAction(action)

    def addToolsMenuSeparator(self):
        return self.window.form.menuTools.addSeparator()
    
    def getNotes(self, query):
        return self.window.col.findNotes(query)

    def getNoteById(self, id):
        return self.window.col.getNote(id)

    def saveMedia(self, path, data):
        return self.window.col.media.writeData(path, data)