"""Static contract checks: python -m unittest discover -s tests -v."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SEAL = 'https://profiles.dunsregistered.com/TpTpmsSeal.aspx?Domain=perifury.com&Directory='

class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

class SealTests(unittest.TestCase):
    def test_all_corporate_footers_use_verified_isolated_seal(self):
        for path in ROOT.glob('*.html'):
            with self.subTest(page=path.name):
                html = path.read_text()
                elements = Elements(html).elements
                frames = [attrs for tag, attrs in elements if tag == 'iframe']
                self.assertEqual(len(frames), 1)
                frame = frames[0]
                self.assertEqual(frame['src'], SEAL)
                self.assertIn('Perifury Private Limited', frame['title'])
                self.assertEqual(set(frame['sandbox'].split()), {
                    'allow-scripts', 'allow-forms', 'allow-popups',
                    'allow-popups-to-escape-sandbox'})
                self.assertEqual(frame['referrerpolicy'], 'strict-origin-when-cross-origin')
                self.assertEqual(frame['loading'], 'lazy')
                self.assertEqual((frame['width'], frame['height']), ('120', '100'))
                self.assertIn('D-U-N-S® Number: 310421130', html)
                self.assertNotIn('SealAuthentication.aspx?Cid=1', html)
                self.assertNotIn('DunsRegisteredProfileAnywhere', html)
                self.assertFalse(any(tag == 'script' and 'dunsregistered' in attrs.get('src', '') for tag, attrs in elements))
                self.assertIn('class="duns-seal"', html.split('<footer>', 1)[1])

if __name__ == '__main__':
    unittest.main()
