INFLECTIONS = {
    'う': ['わ', 'い', 'え', 'お' 'っ'],
    'す': ['さ', 'し', 'せ', 'そ'],
    'く': ['か', 'き', 'け', 'こ', 'い'],
    'ぐ': ['が', 'ぎ', 'げ', 'ご', 'い'],
    'つ': ['た', 'ち', 'て', 'と', 'っ'],
    'ぶ': ['ば', 'び', 'べ', 'ぼ', 'い'],
    'む': ['ま', 'み', 'め', 'も', 'ん'],
    'ぬ': ['な', 'に', 'ね', 'の', 'ん'],
    'る': ['ら', 'り', 'れ', 'ろ', 'っ', 'て', 'た', 'な', 'ち', 'ま', 'よ', 'さ']
}

class Inflector:
    def inflect(self, expression):
        suffix = expression[-1]

        if suffix not in INFLECTIONS:
            return []
    
        root = expression[0:-1]
        inflections = INFLECTIONS[suffix]

        return list(map(lambda inflection: root + inflection, inflections))
