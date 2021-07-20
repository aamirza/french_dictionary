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


def get_dictionary_definition(word, definition_list, definitions, indices, sayings, reflexives):
    logging.debug(f"Definition list from Reverso: {definition_list}")

    if isAlternative(definition_list[0]):
        definition_list = definition_list[1:]

    # get the number of definitions
    indices = list(map(int, indices))  # convert indices to ints
    if len(indices) > 0:
        max_index = max(indices)
    else:
        # If there are no definition numbers, then there's likely only one definition
        max_index = 1

    # cycle through the definitions
    hold_index = 1  # this the definition number.
    held_saying = None  # If the definition is slang, idiom etc.
    reflexive = False  # If the definition is of the reflexive
    dictionary = {}
    for definition in definition_list:
        if definition.startswith('s') and definition in reflexives:  # French reflexive verbs start with s
            reflexive = True
            reflexive_verb = definition
        elif definition in sayings:
            # Sometimes Reverso has parenthesis around the sayings, other times not. For consistency, we'll add it
            # ourselves
            definition.replace("(", "")
            definition.replace(")", "")
            held_saying = definition
        elif definition in definitions:
            dictionary[hold_index] = ''
            if reflexive:
                dictionary[hold_index] += f"({reflexive_verb}) "
            if held_saying:
                dictionary[hold_index] += f"({held_saying}) "
                held_saying = None
            dictionary[hold_index] += definition

            hold_index += 1
            if hold_index > max_index:
                break
    return dictionary


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
