import tempfile
import unittest
from pathlib import Path
from lionelos.book import Book

class BookTests(unittest.TestCase):
    def test_resume_and_order(self):
        with tempfile.TemporaryDirectory() as d:
            b=Book.init(d,'A fictional mystery',2)
            b.add_source('s1','https://example.org','Supplied evidence')
            with self.assertRaises(ValueError): b.accept('draft-001','premature')
            b.accept('research','Dossier')
            self.assertEqual(Book(d).next(),'outline')
            self.assertEqual(Book(d).request()['context']['artifacts']['research'],'Dossier')
            with self.assertRaises(ValueError): b.request(1)
            with self.assertRaises(FileNotFoundError): b.export()

    def test_gate_and_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            b=Book.init(d,'Test',1)
            while b.next() != 'review': b.accept(b.next(),'Chapter')
            cfg={'providers':{'a':{'kind':'static','response':{'verdict':'approve','summary':'Reviewed','findings':[]}}},'agents':[{'name':'a','role':'editor','provider':'a'},{'name':'b','role':'fact checker','provider':'a'},{'name':'c','role':'critic','provider':'a'}]}
            b.review(cfg)
            self.assertTrue(b.export().exists())
            (Path(d)/'artifacts/revision-001.md').write_text('Changed')
            with self.assertRaises(ValueError): b.export()
