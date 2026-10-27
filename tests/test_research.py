import tempfile
import unittest
from unittest.mock import patch
from lionelos.research import Ledger
from lionelos.local_writer import generate

class ResearchTests(unittest.TestCase):
    def bundle(self):
        return {'sources':[dict(id='s',title='Synthetic test source',author='Test',year='2000',url='https://example.org',kind='test')], 'passages':[dict(id='p',source_id='s',locator='p. 1',text='Synthetic evidence')], 'claims':[dict(id='c',statement='Test assertion',kind='fact')], 'evidence':[dict(claim_id='c',passage_id='p',relation='supports')]}
    def test_verification_and_unknown_citation(self):
        with tempfile.TemporaryDirectory() as d:
            l=Ledger(d)
            try:
                l.ingest(self.bundle())
                self.assertFalse(l.audit('Text [claim:c]')['mechanical_checks_passed'])
                l.verify('c'); self.assertTrue(l.audit('Text [claim:c]')['mechanical_checks_passed'])
                self.assertFalse(l.audit('Text [claim:unknown]')['mechanical_checks_passed'])
                self.assertFalse(l.audit('No markers')['mechanical_checks_passed'])
                self.assertEqual(l.packet(['c'])[0]['evidence'][0][0],'supports')
            finally: l.close()
    def test_transaction_and_foreign_key(self):
        with tempfile.TemporaryDirectory() as d:
            l=Ledger(d)
            try:
                b=self.bundle(); b['passages'][0]['source_id']='missing'
                with self.assertRaises(Exception): l.ingest(b)
                self.assertEqual(l.db.execute('SELECT count(*) FROM sources').fetchone()[0],0)
            finally: l.close()
    def test_local_limits_before_network(self):
        with patch('urllib.request.build_opener') as network:
            with self.assertRaises(ValueError): generate({'text':'x'*7000})
            with self.assertRaises(ValueError): generate({},'model:cloud')
            network.assert_not_called()
    def test_adapter_uses_local_endpoint_and_rejects_incomplete(self):
        import json
        from unittest.mock import MagicMock
        opener=MagicMock()
        response=opener.open.return_value.__enter__.return_value
        response.read.return_value=json.dumps({'done':True,'done_reason':'stop','message':{'content':'Evidence-based text'}}).encode()
        with patch('urllib.request.build_opener',return_value=opener):
            self.assertEqual(generate({'job':'test'}),'Evidence-based text')
            request=opener.open.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:11434/api/chat')
            self.assertTrue(json.loads(request.data)['think'])
            response.read.return_value=json.dumps({'done':True,'done_reason':'length','response':'cut'}).encode()
            with self.assertRaises(ValueError): generate({})
