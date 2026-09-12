"""No model calls: compare native sandbox cwd with PowerShell path spelling."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from experiment import BINARY, POINTER, read, runner, save

root = Path(read(POINTER)['root'])
job = read(root / 'fees-B/request.json')
shell = shutil.which('powershell.exe')
scripts = {
    'initial_location': '(Get-Location).Path',
    'normal_location': "$ErrorActionPreference='Stop'; Set-Location -LiteralPath '" + job['cwd'] + "'; (Get-Location).Path",
    'doubled_location': "$ErrorActionPreference='Stop'; Set-Location -LiteralPath '" + job['cwd'].replace('\\', '\\\\') + "'; (Get-Location).Path",
    'forward_location': "$ErrorActionPreference='Stop'; Set-Location -LiteralPath '" + Path(job['cwd']).as_posix() + "'; (Get-Location).Path",
}
result = {'requested_cwd': job['cwd'], 'checks': {}}
for label, script in scripts.items():
    argv = runner.build_check(str(BINARY), job,
                             {'argv': [shell, '-NoProfile', '-NonInteractive', '-Command', script]})
    p = subprocess.run(argv, cwd=job['cwd'], env=runner.worker_env('codex'), capture_output=True,
                       text=True, encoding='utf-8', timeout=30)
    result['checks'][label] = {'argv': argv, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    print(json.dumps({'check': label, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}))
save(root / 'runtime-cwd-preflight-edit.json', result)
