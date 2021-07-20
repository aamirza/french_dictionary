import pytest

from reverso import ReversoDictionary


class TestReverso:
    reverso = ReversoDictionary()
    
    def test_correct_base_reverso_url(self, mocker):
        mocker.patch('reverso.UserAgent')
        assert self.reverso.base_url == "https://mobile-dictionary.reverso.net/french-definition/"

    def test_correct_definition_reverso_url(self, mocker):
        mocker.patch('reverso.UserAgent')
        assert self.reverso._word_url("aléatoire") == \
               "https://mobile-dictionary.reverso.net/french-definition/al%C3%A9atoire"

    @pytest.mark.slow
    def test_retrieves_definition(self):
        definitions = self.reverso._get_word_definition_list('danser')
        assert definitions == {1: "exécuter une danse, bouger son corps en suivant un rythme musical",
                               2: "onduler, se mouvoir en parlant de choses, d'animaux ou d'éléments naturels",
                               3: "(se danser) être dansé"}
