"""Offline bounds for the fresh comparison; no CLI/provider calls."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import three_arm as trial


class Bounds(unittest.TestCase):
    def test_luna_model_override_preserves_max_and_old_default(self):
        for model in (None, 'gpt-6-luna', 'gpt-5.6-luna'):
            with self.subTest(model=model), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root/'luna/worker/task').mkdir(parents=True)
                (root/'implement-prompt.txt').write_text('fixture')
                trial.save(root/'luna/worker/implement-process.json',
                           {'ownership_check_required': True, 'exit_code': None})
                manifest = {'config': ['-c', 'model_reasoning_effort="high"']}
                if model:
                    manifest['luna_model'] = model
                with patch.object(trial.pair, 'sol', return_value='session') as call:
                    result = trial.run_arm(root, manifest, 'luna')
                call.assert_called_once()
                request = call.call_args.args[1]
                self.assertEqual(request['model'], model or 'gpt-5.6-luna')
                self.assertIn('model_reasoning_effort="max"', request['config'])
                self.assertEqual(result['status'], 'failed')

    def test_solo_gets_one_session_and_partial_is_not_qualified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'solo/delegated'
            (folder/'task').mkdir(parents=True)
            (root/'implement-prompt.txt').write_text('fixture')
            trial.save(folder/'implement-final.txt', {'status': 'partial', 'blockers': []})
            with patch.object(trial.pair, 'sol', return_value='session') as model, \
                 patch.object(trial.pair.kd, 'git', return_value='head'), \
                 patch.object(trial.pair.kd, 'changed_files', return_value=[]), \
                 patch.object(trial, 'grade', return_value={'passed': True}):
                result = trial.run_arm(root, {}, 'solo')
            model.assert_called_once()
            self.assertEqual(result['status'], 'finished')
            self.assertFalse(result['qualified'])

    def test_uncertain_worker_ownership_never_starts_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'mimo/delegated/task').mkdir(parents=True)
            kr = root/'kilo'
            kr.mkdir()
            (root/'implement-prompt.txt').write_text('fixture')
            trial.save(kr/'manifest.json', {'lock': str(kr/'lock')})
            trial.save(kr/'receipt.json', {'ownership_check_required': True})
            with patch.object(trial.pair.kd, 'execute') as worker, patch.object(trial.pair, 'sol') as model:
                result = trial.run_arm(root, {'kilo_run_dir': str(kr)}, 'mimo')
            worker.assert_called_once()
            model.assert_not_called()
            self.assertEqual(result['status'], 'failed')

    def test_ownership_scope_rejects_checker_and_arbitrary_tests(self):
        self.assertTrue(trial.allowed('tests/test_worker_batch.py'))
        self.assertTrue(trial.allowed('inventory/ledger.py'))
        for name in ('tests/test_public.py', 'tests/test_other.py', 'inventory/projection.py', '../ledger.py'):
            self.assertFalse(trial.allowed(name))


if __name__ == '__main__':
    unittest.main()
