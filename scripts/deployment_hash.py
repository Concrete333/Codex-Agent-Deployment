"""Read-only artifact hashing inside a Codex sandbox; never import checkout code."""
import hashlib
import json
from pathlib import Path
import sys


def fingerprint(root, names):
    root = Path(root).resolve(strict=True)
    result = {}
    for name in names:
        relative = Path(name)
        if not name or relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Artifact must be a relative file path')
        path = (root / relative).resolve(strict=True)
        if root not in path.parents or not path.is_file():
            raise ValueError('Artifact outside checkout or not a file')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        result[name] = digest.hexdigest()
    return result


if __name__ == '__main__':
    request = json.load(sys.stdin)
    print(json.dumps(fingerprint(request['root'], request['names'])))
