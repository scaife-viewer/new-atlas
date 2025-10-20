from pathlib import Path

from django.test import TestCase

from ..ingestion import _process_dictionary_dir
from ..views import entry_list


class DictionaryTestCase(TestCase):
    def setUp(self):
        path = Path("atlas/dictionaries/tests/test-lsj")

        _process_dictionary_dir(path)

    def test_entry_list(self):
        """
        entry_list returns a list of entries for the given dictionary
        """

        response = self.client.get("/dictionaries/lsj/entries")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]["entries"]), 20)

    def test_entry_list_with_search(self):
        """
        entry_list with a q param filters the results
        """

        response = self.client.get('/dictionaries/lsj/entries?q=θλι')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()["data"]["entries"]) > 0)
