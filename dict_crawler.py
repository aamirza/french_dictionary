from lxml import html
from fake_useragent import UserAgent
import os
import pyperclip
import requests
import readline
import sys
import time


def isNum(var):
    try:
        int(var)
        return True
    except ValueError:
        return False


def isSaying(catch):
    sayings = ('au sens figuré', 'par extension', 'vieilli', 'familier',
               'langage soutenu', "dans l'absolu", 'argot', 'armée',
               'mot américain, armée', 'mot américain', 'péjorativement',
               'populairement', 'ancien', 'Canada', 'Bélgique', 'mécanique',
               'très familièrement', 'par plaisanterie', 'grossièrement')
    if list(catch)[0] == '(' and list(catch)[-1] == ')':
        return catch
    for saying in sayings:
        if saying in catch:
            return str('('+catch+')')
    return False


def isReflexive(catch, word):
    split = catch.split()
    try:
        if split[0] in ('se') and split[1] == word:
            return True
        elif list(word)[0] in ('a', 'e', 'i', 'o', 'u', 'h'):
            split = catch.split("'")
            if split[0] == "s" and split[1] == word:
                return True
    except IndexError:
        pass
    return False

def isAlternative(word):
    if list(word)[0] == ',':
        return True
    else:
        return False


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
    file_path = "/Users/aamir/Documents/code/python/anki_sentences/"
    file_name = time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ".tsv"
    #[{sentence: lala, words: {word1: {word: word1, def: def1}, word2: {word: word2, def: deg2}}}]
    csv = ""
    for card in deck:
        phrase = card['sentence'].replace('"', '""')
        word1 = card['words']['word1']['word'].replace('"', '""')
        def1 = card['words']['word1']['definition'].replace('"', '""')
        word2 = card['words']['word2']['word'].replace('"', '""')
        def2 = card['words']['word2']['definition'].replace('"', '""')
        #format: "sentence"\t"word1"\t"def1"\t""\t"word2"\t"def2"\t""\n
        #csv += phrase+"\t"+word1+"\t"+def1+"\t\t"+word2+"\t"+def2+"\t\n"
        csv += '\"{}\",\"{}\",\"{}\",\"\",\"{}\",\"{}\",\"\"\n'.format(phrase, word1, def1, word2, def2)
    f = open(file_path+file_name, "w")
    f.write(csv)
    f.close()
    print("File exported!")


def convert_french_list_to_utf8(definition_list):
    try:
        return [word.encode("ISO-8859-1").decode('utf-8') for word in
                definition_list]
    except UnicodeDecodeError:
        return definition_list


def main(word, user_agent):
    site = "http://mobile-dictionary.reverso.net/french-definition/"
    site += word
    site = site.encode('utf-8')
    headers = {'User-Agent': user_agent}
    page = requests.get(site, headers=headers)
    tree = html.fromstring(page.content)
    catch = tree.xpath('//span[@direction="target"]/text() | '
                       '//span[@style="background-color:#000000"]/text() | ' 
                       '//span[@style="color:#008000;"]/text() | ' 
                       '//span[@style="color:#0000ff;"]/text()')

    catch = convert_french_list_to_utf8(catch)
    print(catch)  # needed for now for debugging
    if isAlternative(catch[0]):
        del catch[0]

    numbered = False
    definitions = {}

    hold_num = 0
    hold_saying = ''
    reflexive = False
    for definition in catch:
        if isNum(definition) or isSaying(definition) or isReflexive(
                definition, word):
            numbered = True
            if isReflexive(definition, word):
                reflexive = True
                reflexive_term = definition
                continue
            if isSaying(definition):
                hold_saying = isSaying(definition)
                continue
            if int(definition) > hold_num:
                hold_num = int(definition)
                print(hold_num)
            else:
                numbered = False
                continue
        else:
            if numbered:
                if hold_saying and not reflexive:
                    if not hold_num:
                        hold_num += 1
                    definitions[str(hold_num)] = hold_saying + " " + definition
                    numbered = False
                    hold_saying = ''
                    continue
                if reflexive:
                    if not hold_num:
                        hold_num += 1
                    if not hold_saying:
                        definitions[str(hold_num)] = "({}) {}".format(
                            reflexive_term,
                            definition)
                    else:
                        definitions[str(hold_num)] = "({}) {} {}".format(
                            reflexive_term,
                            hold_saying,
                            definition)
                        hold_saying = ''
                    numbered = False
                    continue
                definitions[str(hold_num)] = definition
                numbered = False
                continue
            else:
                if not hold_num:
                    hold_num += 1
                    definitions[str(hold_num)] = definition
                else:
                    break

    message = ''
    print("\n" + word + "\n")
    for x in range(1, len(definitions.keys()) + 1):
        try:
            message += '{} - {}\n'.format(x, definitions[str(x)])
        except KeyError:
            continue
        # print('{} – {}'.format(x, definitions[str(x)]))
    print(message)
    pyperclip.copy(message)

ua = UserAgent(verify_ssl=False)
headers = ua.firefox
collected = []

try:
    main(sys.argv[1], headers)
except IndexError:
    while True:
        try:
            word = input('>>> ')
            if word.find('sss') >= 0:
                # This means that this is a sentence we want to parse
                word = word[word.find('sss')+4:]  # Get rid of the sss
                sentence, to_search = extract_words(word) # it works!
                print(to_search)
                #[{sentence: lala, words: {word1: def1, word2, deg2}}]
                card = {'sentence': sentence, 'words': {
                'word1': {'word': "", 'definition': ""},
                'word2': {'word': "", 'definition': ""}
                }}
                for index, search in enumerate(to_search, 1):
                    try:
                        main(search, headers)
                    except:
                        print("There was an error.")
                        if collected:
                            print("I will export your CSV")
                    card['words']['word'+str(index)]['word'] = search
                    card['words']['word'+str(index)]['definition'] = pyperclip.paste()
                collected.append(card)
                continue
            word = word.replace(' ', '')
            if word.upper() in ('QUIT', 'EXIT', 'DONE'):
                if collected:
                    create_tsv(collected)
                break
            elif word.upper() == 'CLEAR':
                os.system('clear')
                continue
            main(word, headers)
        except Exception as e:
            print(f"{repr(e)}: {e}")
            continue
            #if collected:
            #    print("Saving what you have...")
            #    create_tsv(collected)
