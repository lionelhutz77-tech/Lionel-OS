"""Local evidence ledger. Mechanical validity is not historical truth."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL,
 year TEXT NOT NULL, url TEXT NOT NULL, kind TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS passages(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
 locator TEXT NOT NULL, text TEXT NOT NULL, digest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY, statement TEXT NOT NULL,
 kind TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'unverified');
CREATE TABLE IF NOT EXISTS evidence(claim_id TEXT REFERENCES claims(id), passage_id TEXT REFERENCES passages(id),
 relation TEXT NOT NULL, PRIMARY KEY(claim_id, passage_id, relation));
'''

class Ledger:
    def __init__(self, root):
        self.root=Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.root/'research.sqlite')
        self.db.execute('PRAGMA foreign_keys=ON'); self.db.executescript(SCHEMA)

    def close(self): self.db.close()

    def ingest(self, data):
        """Import a curated source bundle transactionally; no invented verification."""
        with self.db:
            for s in data.get('sources',[]):
                values=[s[k] for k in ('id','title','author','year','url','kind')]
                if not all(isinstance(v,str) and v.strip() for v in values): raise ValueError('source metadata missing')
                self.db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?)', values)
            for p in data.get('passages',[]):
                if not p['locator'].strip() or not p['text'].strip(): raise ValueError('exact locator and passage required')
                self.db.execute('INSERT INTO passages VALUES(?,?,?,?,?)', (p['id'],p['source_id'],p['locator'],p['text'],hashlib.sha256(p['text'].encode()).hexdigest()))
            for c in data.get('claims',[]):
                if c['kind'] not in ('fact','interpretation','hypothesis','normative') or not c['statement'].strip(): raise ValueError('invalid claim')
                self.db.execute('INSERT INTO claims(id,statement,kind) VALUES(?,?,?)',(c['id'],c['statement'],c['kind']))
            for e in data.get('evidence',[]):
                if e['relation'] not in ('supports','contradicts','qualifies'): raise ValueError('invalid evidence relation')
                self.db.execute('INSERT INTO evidence VALUES(?,?,?)',(e['claim_id'],e['passage_id'],e['relation']))

    def verify(self, claim_id):
        """Explicit human attestation after checking original and counterevidence."""
        if not self.db.execute("SELECT 1 FROM evidence WHERE claim_id=? AND relation='supports'",(claim_id,)).fetchone(): raise ValueError('support required')
        with self.db:
            cursor=self.db.execute("UPDATE claims SET status='verified' WHERE id=?",(claim_id,))
            if cursor.rowcount != 1: raise ValueError('unknown claim')

    def packet(self, claim_ids):
        result=[]
        for identifier in claim_ids:
            claim=self.db.execute('SELECT id,statement,kind,status FROM claims WHERE id=?',(identifier,)).fetchone()
            if not claim: raise ValueError('unknown claim '+identifier)
            passages=self.db.execute('''SELECT e.relation,p.id,p.locator,p.text,s.title,s.author,s.year,s.url
              FROM evidence e JOIN passages p ON p.id=e.passage_id JOIN sources s ON s.id=p.source_id
              WHERE e.claim_id=? ORDER BY e.relation,p.id''',(identifier,)).fetchall()
            result.append({'claim':claim,'evidence':passages})
        return result

    def audit(self, manuscript):
        ids=list(dict.fromkeys(re.findall(r'\[claim:([^\]\s]+)\]',manuscript)))
        errors=[]
        if not ids: errors.append('no claim markers; citation coverage cannot be established')
        for identifier in ids:
            row=self.db.execute('SELECT kind,status FROM claims WHERE id=?',(identifier,)).fetchone()
            if not row: errors.append('unknown claim: '+identifier); continue
            if row[0] in ('fact','interpretation') and row[1]!='verified': errors.append('unverified claim: '+identifier)
            if row[0] in ('fact','interpretation') and not self.db.execute("SELECT 1 FROM evidence WHERE claim_id=? AND relation='supports'",(identifier,)).fetchone(): errors.append('unsupported claim: '+identifier)
        for identifier,text,digest in self.db.execute('SELECT id,text,digest FROM passages'):
            if hashlib.sha256(text.encode()).hexdigest()!=digest: errors.append('passage changed: '+identifier)
        return {'mechanical_checks_passed':not errors,'errors':errors,'marked_claims':len(ids),
                'limitations':'Cannot detect all unmarked factual assertions or establish truth, source quality or causal validity.'}

def main(argv=None):
    parser=argparse.ArgumentParser(description='Private research ledger')
    parser.add_argument('project',type=Path)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('init')
    p=sub.add_parser('import'); p.add_argument('bundle',type=Path)
    p=sub.add_parser('packet'); p.add_argument('claims',nargs='+')
    p=sub.add_parser('audit'); p.add_argument('manuscript',type=Path)
    p=sub.add_parser('verify'); p.add_argument('claim'); p.add_argument('--original-checked',action='store_true',required=True)
    args=parser.parse_args(argv); ledger=Ledger(args.project)
    try:
        if args.action=='import': ledger.ingest(json.loads(args.bundle.read_text(encoding='utf-8-sig')))
        if args.action=='verify': ledger.verify(args.claim)
        if args.action=='packet': print(json.dumps(ledger.packet(args.claims),ensure_ascii=False,indent=2))
        if args.action=='audit':
            report=ledger.audit(args.manuscript.read_text(encoding='utf-8-sig')); print(json.dumps(report,ensure_ascii=False,indent=2))
            return 0 if report['mechanical_checks_passed'] else 3
        return 0
    except (ValueError,KeyError,OSError,sqlite3.Error) as exc: parser.exit(2,f'research: {exc}\n')
    finally: ledger.close()

if __name__=='__main__': raise SystemExit(main())
