from pathlib import Path

from django.test import TestCase

from ..ingestion import _process_commentary_dir


class CommentaryTestCase(TestCase):
    def setUp(self):
        path = Path("atlas/commentaries/tests/test-jebb")

        _process_commentary_dir(path)

    def test_passage_view(self):
        """
        passage_view returns a Paginator object with
        `results` containing commentary entries matching
        the supplied `urn`.
        """

        response = self.client.get('/commentaries/passage/urn:cts:greekLit:tlg0011.tlg004/')

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(len(data["results"]) > 0)
        self.assertIsInstance(data["total_pages"], int)
        self.assertIsInstance(data["current_page"], int)

