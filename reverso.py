"""
This is the class to handle communicating with the Reverso website.
"""

# TODO: Write a comment for each function
import logging
import urllib

import pyperclip
import requests
from fake_useragent import UserAgent
from lxml import html


logging.basicConfig(level=logging.WARNING)


def isNum(var):
    try:
        int(var)
        return True
    except ValueError:
        return False


def isSaying(definition):
    sayings = ('au sens figuré', 'par extension', 'vieilli', 'familier',
               'langage soutenu', "dans l'absolu", 'argot', 'armée',
               'mot américain, armée', 'mot américain', 'péjorativement',
               'populairement', 'ancien', 'Canada', 'Bélgique', 'mécanique',
               'très familièrement', 'par plaisanterie', 'grossièrement')
    if list(definition)[0] == '(' and list(definition)[-1] == ')':
        return definition
    for saying in sayings:
        if saying in definition:
            return str('(' + definition + ')')
    return False


def isReflexive(definition, word):
    split = definition.split()
    try:
        if split[0] in ('se') and split[1] == word:
            return True
        elif list(word)[0] in ('a', 'e', 'i', 'o', 'u', 'h'):
            split = definition.split("'")
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


def convert_french_list_to_utf8(definition_list):
    try:
        return [word.encode("ISO-8859-1").decode('utf-8') for word in
                definition_list]
    except UnicodeDecodeError:
        return definition_list


def get_dictionary_definition(word, definition_list, definitions, indexes, sayings, alternatives):
    logging.debug(f"Definition list from Reverso: {definition_list}")
    # TODO: Use new parameters instead of inference

    if isAlternative(definition_list[0]):
        definition_list = definition_list[1:]

    numbered = False
    definitions = {}

    hold_num = 0
    hold_saying = ''
    reflexive = False
    for definition in definition_list:
        if isNum(definition) or isSaying(definition) or isReflexive(definition, word):
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
                logging.debug(f"Definition #{hold_num} found")
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

    return definitions


class ReversoDictionary:
    base_url = "https://mobile-dictionary.reverso.net/french-definition/"

    def __init__(self):
        self.headers = {'User-Agent': UserAgent(verify_ssl=False).firefox}  # Needed to make requests
        print(self.copyright_warning())

    def _word_url(self, word):
        """The URL for the specific word"""
        return urllib.parse.quote(self.base_url + word, safe=":/")

    def _get_definition_page_html(self, word):
        page = requests.get(self._word_url(word), headers=self.headers)
        return html.fromstring(page.content)

    def _get_word_definition_list(self, word):
        definition_xpath = '//span[@direction="target"]/text()'
        saying_xpath = '//span[@style="color:#008000;"]/text()'
        index_numbers_xpath = '//span[@style="background-color:#000000"]/text()'
        alternative_words_xpath = '//span[@style="color:#0000ff;"]/text()'
        all_xpaths = f'{definition_xpath} | {saying_xpath} | {index_numbers_xpath} | {alternative_words_xpath}'

        page_html = self._get_definition_page_html(word)
        # TODO: Convert all list to UTF-8
        definitions = page_html.xpath(definition_xpath)
        sayings = page_html.xpath(saying_xpath)
        index_numbers = page_html.xpath(index_numbers_xpath)
        alternative_words = page_html.xpath(alternative_words_xpath)
        definition_list = convert_french_list_to_utf8(page_html.xpath(all_xpaths))

        return get_dictionary_definition(word, definition_list, definitions, index_numbers, sayings, alternative_words)

    def get_word_definitions(self, word, *, copy_to_clipboard=False):
        definitions = self._get_word_definition_list(word)

        message = ''
        print("\n" + word + "\n")

        starting_index = 1
        for index in range(starting_index, len(definitions.keys()) + 1):
            try:
                message += '{} - {}\n'.format(index, definitions[str(index)])
            except KeyError:
                continue
        print(message)

        if copy_to_clipboard:
            pyperclip.copy(message)
        return message
    
    @staticmethod
    def copyright_warning():
        return "WARNING: This program is purely for demonstration and not intended for distribu-\n" \
               "tion. Per Reverso's Condition of Use, you must use Reverso's original site on a\n" \
               "regular web browser. After you are done using this app, please uninstall and re-\n" \
               "move from your system.\n\n" \
               "Reverso Conditions of Use: https://www.reverso.net/disclaimer.aspx?lang=EN \n"
