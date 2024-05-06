from symspellpy import SymSpell, Verbosity

# Initialize SymSpell object
sym_spell = SymSpell(max_dictionary_edit_distance=10, prefix_length=12)

dictionary_path = "frequency_dictionary_en_82_765.txt"

# The term_index and count_index specify the column positions of the word and word frequency
term_index = 0
count_index = 1

# Load the dictionary
sym_spell.load_dictionary(dictionary_path, term_index, count_index)

def spell_check(text):
    for word in text.split():
        suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=10)
        if suggestions:
            text = text.replace(word, suggestions[0].term)
    return text
