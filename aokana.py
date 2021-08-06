from anki.utils import os, json
from aqt.utils import showInfo
from aqt import qt

from .sync.syncer import Syncer
from .sync.confirmer import ChangeConfirmer
from .widgets.syncdialog import SyncDialog
from .arguments.syncarguments import SyncArgumentsFetcher
from .exceptions import SyncArgumentsException

class Aokana():
    def __init__(self, api):
        self.api = api
        self.config = api.getConfig()
        self.syncDialog = self.getSyncDialog()
        self.syncArgumentsFetcher = SyncArgumentsFetcher(self.config, self.api.getNotes, self.syncDialog)
        self.syncer = Syncer(self.onSyncUpdate, self.api.saveMedia)
        self.changeConfirmer = ChangeConfirmer(self.api.saveCollection)
        self.progress = self.api.getProgress()

    def load(self):
        self.api.addToolsMenuSeparator()
        self.addAction('Sync 蒼彼方', self.openSyncDialog, "Ctrl+k")

    def addAction(self, title, callback, shortcut):
        action = qt.QAction(title, self.api.window)
        action.triggered.connect(lambda: callback())
        action.setShortcut(shortcut)
        self.api.addToolsMenuAction(action)

    def getSyncDialog(self):
        dialog = SyncDialog(self.api.window)
        dialog.syncClicked.connect(self.onSyncClicked)
        dialog.confirmClicked.connect(self.onSyncConfirmed)

        return dialog

    def onSyncUpdate(self, message, expression, index):
        print(message)
        self.progress.update('Processed %s...' % expression, index)
    
    def onSyncConfirmed(self, changeOperations, sourceDialog):
        changes = self.changeConfirmer.confirm(changeOperations)
        showInfo('Processed %d note(s) with %d update(s).' % (len(changeOperations), changes), sourceDialog)

    def shouldStopBeforeConfirmation(self, currentNote, changeOperations):
        count = len(changeOperations)
        return currentNote != None and (count == 0 or (count == 1 and not changeOperations[0].hasAnyChanges()))

    def syncEntries(self, currentNote, extendedQuery, skipTagged, resolveManually):
        try:
            args = self.syncArgumentsFetcher.fetch(extendedQuery, skipTagged, resolveManually)
            self.progress.start(sum(len(notePack['notes']) for notePack in args.notePacks), parent=self.syncDialog)
            self.progress._showWin()
            changeOperations = self.syncer.sync(args, lambda: self.progress.want_cancel())
            self.progress.finish()

            if self.shouldStopBeforeConfirmation(currentNote, changeOperations):
                showInfo('No changes available for %s' % currentNote['expression'], self.api.window)
            else:
                self.syncDialog.showConfirmDialog(changeOperations)
        except SyncArgumentsException as e:
            showInfo(e.getMessage(), self.syncDialog)

    def onSyncClicked(self):
        dialog = self.syncDialog
        self.syncEntries(None, dialog.extendedQuery(), dialog.skipTagged(), dialog.resolveManually())

    def openSyncDialog(self):
        note = self.api.getCurrentReviewerNote()

        if note != None and self.api.isNoteOfType(note, self.config['noteType']):
            self.syncEntries(note, 'nid:%d' % note.id, False, True)
            return

        self.syncDialog.exec_()
