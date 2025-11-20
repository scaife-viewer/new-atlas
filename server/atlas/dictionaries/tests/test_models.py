from pathlib import Path

from django.test import TestCase

from ..ingestion import _process_dictionary_dir
from ..models import Dictionary


class DictionaryTestCase(TestCase):
    def setUp(self):
        path = Path("atlas/dictionaries/tests/test-lsj")

        _process_dictionary_dir(path)

        self.dictionary = Dictionary.objects.all()[0]

    def test_search(self):
        """
        Search returns a QuerySet of DictionaryEntries
        matching the query
        """

        results = self.dictionary.search_entries("ἀέθλιον")

        self.assertTrue(len(results) > 0)

        results = self.dictionary.search_entries("θλι")

        self.assertTrue(len(results) > 0)
