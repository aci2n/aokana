class ChangeConfirmer():
    def __init__(self, save):
        self.save = save

    def confirm(self, changeOperations):
        changes = 0

        for changeOperation in changeOperations:
            changed = changeOperation.applyAllChanges()

            if changed:
                changeOperation.flush()
                changes += 1

        if changes > 0:
            self.save()

        return changes

    