"""Generate a reproducible catalogue and an oracle from independent design facts."""
import argparse
import json
from pathlib import Path
import random
import shutil

HERE = Path(__file__).resolve().parent


def emit(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def build(target, truth_path):
    target.mkdir(parents=True, exist_ok=False)
    shutil.copy2(HERE / 'TASK.md', target / 'TASK.md')
    rng = random.Random(190913)
    catalogue = target / 'catalogue'
    owners = {f'group-{i:02}': f'team-{(i * 7 + 3) % 17:02}' for i in range(17)}
    emit(catalogue / 'ownership.json', owners)
    fields = ['event_id', 'customer_id', 'customer_email', 'created_at', 'status',
              'total_minor', 'currency', 'region', 'sku', 'quantity', 'channel',
              'tracking_id', 'postal_area', 'merchant_id', 'campaign', 'trace_id']
    profiles = {}
    for i in range(16):
        selected = rng.sample(fields, 8)
        if i % 2 and 'customer_email' not in selected:
            selected.append('customer_email')
        if not i % 2 and 'customer_email' in selected:
            selected.remove('customer_email')
        profiles[f'profile-{i:02}'] = selected
        emit(catalogue / 'profiles' / f'profile-{i:02}.json', {
            'fields': selected, 'format': 'json', 'version': 3,
            'field_descriptions': {f: f'Exported source field {f}; retain its established serialization.' for f in selected},
            'transport': {'content_type': 'application/json', 'compression': 'gzip', 'batch_limit': 100}})
    findings = []
    reasons = ['missing', 'scope', 'not_started', 'expired', 'revoked', None]
    for i in range(120):
        sid = f'svc-{i:03}'
        profile = f'profile-{rng.randrange(16):02}'
        team = f'group-{rng.randrange(17):02}'
        remove = rng.sample(profiles[profile], rng.randrange(3))
        add = rng.sample(fields, rng.randrange(3))
        if i % 7 == 0:
            remove = list(set(remove) | {'customer_email'})
            remove.sort()
        if i % 11 == 0:
            add = list(set(add) | {'customer_email'})
            add.sort()
        active = i % 9 != 0
        environment = 'staging' if i % 13 == 0 else 'production'
        destination = 'internal' if i % 8 == 0 else 'external'
        override = f'special-owner-{i % 5}' if i % 10 == 0 else ''
        reason = reasons[rng.randrange(len(reasons))]
        # Oracle comes from generation decisions, not parsing the rendered catalogue.
        exports_email = 'customer_email' in add or ('customer_email' in profiles[profile] and 'customer_email' not in remove)
        service = {'service': sid, 'active': active, 'environment': environment,
                   'destination': destination, 'profile': profile, 'team': team,
                   'owner_override': override, 'remove_fields': remove, 'add_fields': add,
                   'endpoint': f'https://partner-{i % 23}.example.invalid/events',
                   'operations': {'retries': 2 + i % 5, 'timeout_seconds': 15 + i % 4,
                                  'queue': f'exports-{i % 12:02}', 'dead_letter': f'dlq-{i % 12:02}',
                                  'oncall_rotation': f'rotation-{i % 17:02}'},
                   'notes': f'Catalogue entry {sid}. Customer email may appear in legacy examples; evaluate the active field set, not this note.'}
        emit(catalogue / 'services' / f'{sid}.json', service)
        if reason != 'missing':
            record = {'service': sid, 'scope': ['customer_email', 'customer_id'],
                      'starts': '2026-01-01', 'expires': '2027-01-01', 'revoked': None}
            if reason == 'scope':
                record['scope'] = ['customer_id']
            elif reason == 'not_started':
                record['starts'] = '2026-09-11'
            elif reason == 'expired':
                record['expires'] = '2026-09-10'
            elif reason == 'revoked':
                record['revoked'] = '2026-09-10'
            elif i % 2:
                record['starts'], record['revoked'] = '2026-09-10', '2026-09-11'
            content = '# Export review ' + sid + '\n\n```json\n' + json.dumps(record, indent=2) + '\n```\n\n'
            content += ('The partner requests these fields for reconciliation. The structured record above defines the actual '
                        'authorization, including start, expiry and any revocation; this narrative does not grant access. '
                        'Operations retain the existing delivery retry settings. A renewal request or informal discussion '
                        'does not extend the recorded interval. Route ownership follows the service catalogue.\n')
            path = catalogue / 'waivers' / f'{sid}.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        if active and environment == 'production' and destination == 'external' and exports_email and reason:
            required = {f'catalogue/services/{sid}.json': sid,
                        f'catalogue/profiles/{profile}.json': '"fields"'}
            if not override:
                required['catalogue/ownership.json'] = team
            if reason != 'missing':
                key = {'scope': 'scope', 'not_started': 'starts', 'expired': 'expires', 'revoked': 'revoked'}[reason]
                required[f'catalogue/waivers/{sid}.md'] = '"' + key + '"'
            findings.append({'service': sid, 'owner': override or owners[team], 'reason': reason,
                             'required_evidence': required})
    emit(truth_path, {'assessed_at': '2026-09-10', 'services_reviewed': 120, 'findings': findings})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=Path)
    parser.add_argument('truth', type=Path)
    args = parser.parse_args()
    build(args.target, args.truth)
