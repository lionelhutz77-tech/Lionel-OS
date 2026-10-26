"""Persistent, resumable book jobs. Project data belongs outside the public repo."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from .config import build_providers
from .models import AgentSpec, TaskSpec
from .orchestrator import Orchestrator

STAGES = ('research', 'outline', 'bible', 'draft', 'revision', 'review')
INSTRUCTIONS = {
 'research': 'Build a research dossier from supplied sources. Record source IDs for claims, distinguish fact, inference and fiction; list unanswered questions. Never invent citations.',
 'outline': 'Plan the complete book including ending, causal plot, character arcs, pacing, chapter objectives, setups and payoffs.',
 'bible': 'Create the canonical character, setting, chronology, rules and continuity reference using the approved outline and research.',
 'draft': 'Write the requested chapter as finished prose, respecting the complete outline, research, bible and previous chapters. Keep voice, causality and continuity consistent.',
 'revision': 'Revise the requested chapter against the whole book. Resolve continuity, motivation, pacing, exposition and repetition issues; preserve established facts.',
 'review': 'Audit the complete manuscript for factual support, unresolved research, continuity, causality, character arcs, pacing, style, repetitions and ending/payoffs. Reject unresolved material problems. Literary quality is a judgment, not a guarantee.'
}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)

class Book:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state_path = self.root / 'book.json'
        self.state = json.loads(self.state_path.read_text(encoding='utf-8'))

    @classmethod
    def init(cls, root, brief, chapters):
        root = Path(root).resolve()
        if not brief.strip() or not 1 <= chapters <= 200:
            raise ValueError('brief and 1..200 chapters required')
        root.mkdir(parents=True, exist_ok=True)
        if (root / 'book.json').exists():
            raise ValueError('project already exists')
        write(root / 'book.json', {'schema_version': 1, 'brief': brief, 'chapters': chapters, 'done': [], 'sources': []})
        return cls(root)

    def jobs(self):
        return ['research', 'outline', 'bible'] + [f'draft-{i:03}' for i in range(1,self.state['chapters']+1)] + [f'revision-{i:03}' for i in range(1,self.state['chapters']+1)] + ['review']

    def next(self):
        return next((j for j in self.jobs() if j not in self.state['done']), None)

    def add_source(self, identifier, url, text):
        if self.state['done']:
            raise ValueError('add sources before starting; create a new project to change research inputs')
        if not identifier.strip() or not url.startswith(('https://','http://')) or not text.strip():
            raise ValueError('source ID, URL and extracted source text required')
        if any(s['id'] == identifier for s in self.state['sources']):
            raise ValueError('duplicate source ID')
        self.state['sources'].append({'id': identifier, 'url': url, 'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest()})
        write(self.state_path, self.state)

    def request(self, max_chars=200000):
        job = self.next()
        if job is None:
            raise ValueError('all jobs finished')
        context = {'brief': self.state['brief'], 'sources': self.state['sources'], 'artifacts': {j: (self.root/'artifacts'/f'{j}.md').read_text(encoding='utf-8') for j in self.state['done']}}
        payload = {'job': job, 'instruction': INSTRUCTIONS[job.split('-')[0]], 'context': context}
        if len(json.dumps(payload, ensure_ascii=False)) > max_chars:
            raise ValueError('context limit exceeded; configure a larger limit or implement verified retrieval; no silent truncation')
        return payload

    def accept(self, job, text):
        if job != self.next() or job == 'review' or not text.strip():
            raise ValueError('only the next non-review job can be imported')
        target = self.root/'artifacts'/f'{job}.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix('.tmp')
        temporary.write_text(text, encoding='utf-8')
        os.replace(temporary, target)
        self.state['done'].append(job)
        write(self.state_path, self.state)

    def run(self, config):
        """Run a trusted, explicitly configured writer adapter; resume after failure."""
        argv = config.get('writer_argv')
        if not isinstance(argv, list) or not argv or not all(isinstance(a,str) and a for a in argv):
            raise ValueError('writer_argv must be an explicit nonempty argument list')
        limit = config.get('max_calls', 20)
        while self.next() != 'review':
            request = self.request(config.get('max_context_chars', 200000))
            calls = self.state.get('calls', 0)
            if calls >= limit:
                raise ValueError('persistent call limit reached; explicitly increase max_calls to continue')
            self.state['calls'] = calls + 1
            write(self.state_path, self.state)
            result = subprocess.run(argv, input=json.dumps(request,ensure_ascii=False), text=True,
                                    encoding='utf-8', capture_output=True, shell=False,
                                    timeout=config.get('timeout_seconds',300), check=False)
            if result.returncode or not result.stdout.strip() or len(result.stdout)>config.get('max_output_chars',100000):
                raise ValueError('writer failed or returned invalid output; job remains pending')
            self.accept(request['job'], result.stdout)
        self.review(config['review'])
        return self.export()

    def digest(self):
        payload = {'state': self.state, 'artifacts': {j:(self.root/'artifacts'/f'{j}.md').read_text(encoding='utf-8') for j in self.state['done'] if j != 'review'}}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def review(self, config):
        if self.next() != 'review':
            raise ValueError('finish all writing jobs first')
        request = self.request(config.get('max_context_chars', 200000))
        providers = build_providers(config['providers'])
        agents = tuple(AgentSpec(**a) for a in config['agents'])
        task = TaskSpec('book-final-review', INSTRUCTIONS['review'], json.dumps(request,ensure_ascii=False))
        report = Orchestrator(providers).run(task, agents, self.root/'review-evidence.json')
        if report.decision != 'accepted':
            raise ValueError('quality gate did not accept manuscript; see review-evidence.json')
        write(self.root/'approval.json', {'manuscript_sha256': self.digest()})

    def export(self):
        approval = json.loads((self.root/'approval.json').read_text())
        if approval['manuscript_sha256'] != self.digest():
            raise ValueError('manuscript changed after review')
        output = '\n\n'.join((self.root/'artifacts'/f'revision-{i:03}.md').read_text(encoding='utf-8') for i in range(1,self.state['chapters']+1))
        target = self.root/'manuscript.md'
        target.write_text(output, encoding='utf-8')
        return target


def main(argv=None):
    parser = argparse.ArgumentParser(description='LionelOS book project jobs')
    parser.add_argument('project', type=Path)
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init'); init.add_argument('--brief', type=Path, required=True); init.add_argument('--chapters', type=int, required=True)
    sub.add_parser('next')
    source = sub.add_parser('source'); source.add_argument('id'); source.add_argument('url'); source.add_argument('text',type=Path)
    accept = sub.add_parser('import'); accept.add_argument('job'); accept.add_argument('text',type=Path)
    review = sub.add_parser('review'); review.add_argument('config',type=Path)
    run = sub.add_parser('run'); run.add_argument('config',type=Path)
    sub.add_parser('export')
    args = parser.parse_args(argv)
    try:
        book = Book.init(args.project,args.brief.read_text(encoding='utf-8'),args.chapters) if args.action == 'init' else Book(args.project)
        if args.action == 'next': print(json.dumps(book.request(),ensure_ascii=False,indent=2))
        if args.action == 'source': book.add_source(args.id,args.url,args.text.read_text(encoding='utf-8'))
        if args.action == 'import': book.accept(args.job,args.text.read_text(encoding='utf-8'))
        if args.action == 'review': book.review(json.loads(args.config.read_text(encoding='utf-8')))
        if args.action == 'run': print(book.run(json.loads(args.config.read_text(encoding='utf-8'))))
        if args.action == 'export': print(book.export())
        return 0
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f'book: {exc}\n')

if __name__ == '__main__':
    raise SystemExit(main())
