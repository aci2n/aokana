from ..sync.changeop import AOKANA_TAG, AOKANA_IGNORE_TAG

class QueryBuilder():
    def build(self, noteType, skipTagged, extendedQuery):
        query = 'note:%s -tag:%s' % (noteType, AOKANA_IGNORE_TAG)

        if skipTagged:
            query += ' -tag:%s' % AOKANA_TAG
        
        if extendedQuery != '':
            query += ' ' + extendedQuery

        return query