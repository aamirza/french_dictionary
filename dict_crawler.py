import os
import sys
import time

from reverso import ReversoDictionary


def extract_words(phrase):
    extracted = []
    while phrase.find("((") >= 0 and phrase.find("))") >= 0:
        time.sleep(0.5)
        search_word = phrase[phrase.find("((")+2:phrase.find("))")]
        conjugated_word = search_word
        if search_word.find("|") >= 0:
            conjugated_word = search_word[0:search_word.find("|")]
            search_word = search_word[search_word.find("|")+1:]
        extracted.append(search_word)
        if conjugated_word != search_word:
            phrase = phrase.replace("(({}|{}))".format(conjugated_word, search_word), conjugated_word)
        else:
            phrase = phrase.replace("(("+conjugated_word+"))", conjugated_word)
    return phrase, extracted


def create_tsv(deck):
    anki_sentences_folder = os.path.join(os.path.dirname(__file__), "anki_sentences")
    if not os.path.exists(anki_sentences_folder):
        os.makedirs(anki_sentences_folder)
    file_name = time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ".tsv"
    file_path = os.path.join(anki_sentences_folder, file_name)
    #[{sentence: lala, words: {word1: {word: word1, def: def1}, word2: {word: word2, def: deg2}}}]
    csv = ""
    for card in deck:
        phrase = card['sentence'].replace('"', '""')
        word1 = card['words']['word1']['word'].replace('"', '""')
        def1 = card['words']['word1']['definition'].replace('"', '""')
        word2 = card['words']['word2']['word'].replace('"', '""')
        def2 = card['words']['word2']['definition'].replace('"', '""')
        csv += '\"{}\",\"{}\",\"{}\",\"\",\"{}\",\"{}\",\"\"\n'.format(phrase, word1, def1, word2, def2)

    with open(file_path, "w+") as f:
        f.write(csv)

    print(f"File exported to {file_path}!")


collected = []
reverso = ReversoDictionary()

try:
    word_to_search = sys.argv[1]
    reverso.get_word_definitions(word_to_search, copy_to_clipboard=True)
except IndexError:
    while True:
        try:
            word = input('>>> ')
            if word.find('sss') >= 0:
                # This means that this is a sentence we want to parse
                word = word[word.find('sss')+4:]  # Get rid of the sss
                sentence, to_search = extract_words(word) # it works!
                #print(to_search)
                #[{sentence: lala, words: {word1: def1, word2, deg2}}]
                card = {'sentence': sentence, 'words': {
                'word1': {'word': "", 'definition': ""},
                'word2': {'word': "", 'definition': ""}
                }}
                for index, search in enumerate(to_search, 1):
                    try:
                        definition = reverso.get_word_definitions(search)
                    except:
                        print("There was an error.")
                        if collected:
                            print("I will export your CSV")
                        definition = ""
                    card['words']['word' + str(index)]['word'] = search
                    card['words']['word' + str(index)]['definition'] = definition
                collected.append(card)
                continue
            if word.upper() in ('QUIT', 'EXIT', 'DONE'):
                if collected:
                    create_tsv(collected)
                break
            elif word.upper() == 'CLEAR':
                os.system('clear')
                continue
            reverso.get_word_definitions(word, copy_to_clipboard=True)
        except Exception as e:
            # TODO: Create timeout error
            print(f"{repr(e)}: {e}")
            continue
