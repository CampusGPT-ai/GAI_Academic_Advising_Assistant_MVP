import spacy
from textblob import TextBlob
from spellchecker import SpellChecker

def spell_check(text):
    spell = SpellChecker()
    # Find those words that may be misspelled
    strip_text = text.replace("?","").replace(".","").replace(",","").replace("!","").replace(";","").replace(":","").replace("(","").replace(")","").replace("[","").replace("]","").replace("{","").replace("}","")
    misspelled = spell.unknown(strip_text.split())

    for word in misspelled:
        suggestion = spell.correction(word)
        text = text.replace(word, suggestion)
    
    return text

def remove_plural(text):
    word_list = []
    for word in text:
        word_new = word[:-1] if word.endswith("s") else word
        word_list.append(word_new)
    return word_list

def extract_keywords(text):
    text = spell_check(text)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "VERB")]
    keywords = remove_plural(keywords)
    keywords = list(set(keywords))
    return keywords

if __name__ == "__main__":
    print(extract_keywords("What interships are available at Microsoft?"))
