from aqt import qt

class ConflictResolver():
    pass

class AutomaticConflictResolver(ConflictResolver):
    def resolve(self, note, matches):
        return matches[0]

class ManualConflictResolver(ConflictResolver):
    def __init__(self, dialog):
        self.dialog = dialog

    def resolve(self, note, matches):
        result = None
        items = []

        for i, match in enumerate(matches):
            items.append('%d: [%s] - %s' % (i, match.key, match.text))

        message = 'Resolve conflict for %s' % note['expression']
        choice, success = qt.QInputDialog.getItem(self.dialog, message, 'Matches', items, editable=False)

        if success:
            index = int(choice.split(':', 1)[0])
            result =  matches[index]

        return result