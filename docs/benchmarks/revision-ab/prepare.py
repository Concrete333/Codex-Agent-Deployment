"""Freeze the skill, generate the audit corpus, and validate its independent oracle.

No model calls. Private paths and answer files stay in a unique temporary folder.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def audit_from_rendered_source(root):
    """Independent reader, never consulting the generator's design facts."""
    owners = json.loads((root / 'catalogue/ownership.json').read_text())
    findings = []
    inventory = sorted((root / 'catalogue/services').glob('*.json'))
    for service_path in inventory:
        service = json.loads(service_path.read_text())
        profile_path = root / 'catalogue/profiles' / (service['profile'] + '.json')
        profile = json.loads(profile_path.read_text())
        fields = set(profile['fields'])
        fields.difference_update(service['remove_fields'])
        fields.update(service['add_fields'])
        if not (service['active'] and service['environment'] == 'production'
                and service['destination'] == 'external' and 'customer_email' in fields):
            continue
        waiver_path = root / 'catalogue/waivers' / (service['service'] + '.md')
        evidence = {service_path: service['service'], profile_path: '"fields"'}
        reason, key = 'missing', None
        if waiver_path.is_file():
            record = json.loads(waiver_path.read_text().split('```json', 1)[1].split('```', 1)[0])
            if 'customer_email' not in record['scope'] or record['service'] != service['service']:
                reason, key = 'scope', 'scope'
            elif record['starts'] > '2026-09-10':
                reason, key = 'not_started', 'starts'
            elif record['expires'] <= '2026-09-10':
                reason, key = 'expired', 'expires'
            elif record['revoked'] is not None and record['revoked'] <= '2026-09-10':
                reason, key = 'revoked', 'revoked'
            else:
                continue
            evidence[waiver_path] = '"' + key + '"'
        if service['owner_override']:
            owner = service['owner_override']
        else:
            owner = owners[service['team']]
            evidence[root / 'catalogue/ownership.json'] = service['team']
        citations = []
        for path, needle in evidence.items():
            line = next(i for i, text in enumerate(path.read_text().splitlines(), 1) if needle in text)
            citations.append({'path': path.relative_to(root).as_posix(), 'line': line})
        findings.append({'service': service['service'], 'owner': owner, 'reason': reason, 'evidence': citations})
    return {'assessed_at': '2026-09-10', 'services_reviewed': len(inventory), 'findings': findings}


def main():
    local = HERE / 'local-fixture.json'
    if local.exists():
        raise SystemExit('Frozen fixture already exists; reuse it instead of regenerating during trials.')
    run = Path(tempfile.mkdtemp(prefix='agent-deployment-revision-ab-'))
    policy = run / 'policy'
    policy.mkdir()
    shutil.copy2(REPO / 'SKILL.md', policy / 'SKILL.md')
    for name in ('references', 'scripts'):
        shutil.copytree(REPO / name, policy / name, ignore=shutil.ignore_patterns('__pycache__'))
    spec = importlib.util.spec_from_file_location('build_catalogue', HERE / 'investigation/build.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    source, truth = run / 'investigation-source', run / 'investigation-truth.json'
    builder.build(source, truth)
    reference = run / 'investigation-reference'
    shutil.copytree(source, reference)
    save(reference / 'answer.json', audit_from_rendered_source(reference))
    fixture = {'root': str(run), 'skill_source': str(policy), 'python': sys.executable,
               'investigation_source': str(source), 'investigation_truth': str(truth),
               'investigation_reference': str(reference),
               'policy_sha256': {p.relative_to(policy).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(policy.rglob('*')) if p.is_file()}}
    save(local, fixture)
    for suite, target in [('repair', HERE / 'repair/reference'), ('investigation', reference)]:
        subprocess.run([sys.executable, '-B', str(HERE / suite / 'grade.py'), str(target)], check=True)
    # Deliberately wrong reports must fail without changing the oracle or grader.
    answer = json.loads((reference / 'answer.json').read_text())
    assert len(answer['findings']) >= 15, 'Fixture has too few meaningful findings'
    mutants = {
        'missing-finding': dict(answer, findings=answer['findings'][1:]),
        'wrong-coverage': dict(answer, services_reviewed=119),
        'missing-citations': dict(answer, findings=[dict(row, evidence=[]) for row in answer['findings']]),
        'wrong-reason': dict(answer, findings=[dict(row, reason='missing') for row in answer['findings']]),
    }
    for label, mutant in mutants.items():
        save(reference / 'answer.json', mutant)
        checked = subprocess.run([sys.executable, '-B', str(HERE / 'investigation/grade.py'), str(reference)],
                                 capture_output=True, text=True)
        (run / (label + '.log')).write_text(checked.stdout + checked.stderr, encoding='utf-8')
        if checked.returncode == 0:
            raise RuntimeError('Grader accepted mutant: ' + label)
    save(reference / 'answer.json', answer)
    print(json.dumps({'frozen': str(local), 'private_root': str(run),
                      'services': 120, 'findings': len(answer['findings']), 'rejected_mutants': len(mutants),
                      'catalogue_bytes': sum(p.stat().st_size for p in (source / 'catalogue').rglob('*') if p.is_file())}))


if __name__ == '__main__':
    main()
