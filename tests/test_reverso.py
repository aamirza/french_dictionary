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
