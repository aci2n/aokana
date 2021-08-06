INFLECTIONS = {
    'う': ['わ', 'い', 'う', 'え', 'お' 'っ'],
    'す': ['さ', 'し', 'す', 'せ', 'そ'],
    'く': ['か', 'き', 'く', 'け', 'こ', 'い'],
    'ぐ': ['が', 'ぎ', 'ぐ', 'げ', 'ご', 'い'],
    'つ': ['た', 'ち', 'つ', 'て', 'と', 'っ'],
    'ぶ': ['ば', 'び', 'ぶ', 'べ', 'ぼ', 'い'],
    'む': ['ま', 'み', 'む', 'め', 'も', 'ん'],
    'ぬ': ['な', 'に', 'ぬ', 'ね', 'の', 'ん'],
    'る': ['ら', 'り', 'る', 'れ', 'ろ', 'っ', 'て', 'た', 'な', 'ち', 'ま', 'よ', 'さ']
}

class Inflector:
    def inflect(self, expression):
        suffix = expression[-1]

        if suffix not in INFLECTIONS:
            return []
    
        root = expression[0:-1]
        inflections = INFLECTIONS[suffix]

        return map(lambda inflection: root + inflection, inflections)
