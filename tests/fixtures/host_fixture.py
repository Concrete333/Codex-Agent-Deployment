"""Offline host process for transport qualification; never launches a model CLI."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import deployment_host as host
import deployment_runner as runner

job, state, bridge = sys.argv[1:]
raw = runner.read_json(job)
with patch.object(runner, "preflight"), patch.object(runner, "run", return_value={
        "id": raw["id"], "status": "ready_for_review", "accepted": False, "offline_fixture": True}):
    result = host.serve(raw, Path(state), Path(bridge), sys.executable, 60,
                        on_ready=lambda packet: print(json.dumps(packet), flush=True))
print(json.dumps(result), flush=True)
