"""Offline pipeline stop/duplicate guards; no model calls."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import pipeline as p


class PipelineBounds(unittest.TestCase):
    def test_failed_implementation_never_starts_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pointer=root/'pointer.json'
            p.save(pointer,dict(root=str(root)))
            p.save(root/'pipeline-plan.json',dict(pinned={}))
            p.save(root/'batch-status.json',dict(status='needs_attention'))
            with patch.object(p,'POINTER',pointer),patch.object(p.implementation,'POINTER',pointer), \
                 patch.object(p.implementation,'run') as impl,patch.object(p.acceptance,'prepare') as review:
                with self.assertRaises(RuntimeError): p.run()
                impl.assert_called_once(); review.assert_not_called()
                self.assertEqual(p.read(root/'pipeline-status.json')['phase'],'needs_attention')
                with self.assertRaises(FileExistsError): p.run()
                impl.assert_called_once(); review.assert_not_called()

    def test_changed_frozen_input_never_starts_implementation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pointer=root/'pointer.json'; source=root/'input.txt'
            source.write_text('changed')
            p.save(pointer,dict(root=str(root)))
            p.save(root/'pipeline-plan.json',dict(pinned={str(source):'incorrect-hash'}))
            with patch.object(p,'POINTER',pointer),patch.object(p.implementation,'run') as impl:
                with self.assertRaises(ValueError): p.run()
                impl.assert_not_called()
                self.assertFalse((root/'pipeline-started.json').exists())


if __name__=='__main__': unittest.main()
