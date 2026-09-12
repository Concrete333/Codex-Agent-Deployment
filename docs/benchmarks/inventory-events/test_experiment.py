"""Offline dispatch bounds; never start a CLI or model."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import experiment as e


class DispatchBounds(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.pointer=self.root/'pointer.json'
        e.save(self.pointer,dict(root=str(self.root)))
        e.save(self.root/'manifest.json',dict(state=str(self.root/'state'),order=['solo','worker'],frozen={}))
        for arm in ['solo','worker']:
            (self.root/arm).mkdir()
            e.save(self.root/arm/'request.json',dict(id=arm))
        self.patcher=patch.object(e,'POINTER',self.pointer)
        self.patcher.start(); self.addCleanup(self.patcher.stop)

    def run_case(self,first,second):
        with patch.object(e,'solo',return_value=first) as solo, patch.object(e.runner,'run',return_value=second) as worker, \
             patch.object(e,'packet') as packet, patch.object(e,'summarize'):
            if first['status'] in ('blocked','partial'):
                with self.assertRaises(RuntimeError): e.run()
            else: e.run()
            return solo.call_count,worker.call_count,packet.call_count

    def test_two_attempts_then_duplicate_refused(self):
        ready=dict(status='ready_for_review',ownership_check_required=False)
        self.assertEqual(self.run_case(ready,ready),(1,1,2))
        with patch.object(e,'solo') as solo, self.assertRaises(FileExistsError): e.run()
        solo.assert_not_called()

    def test_checks_failure_does_not_retry(self):
        self.assertEqual(self.run_case(dict(status='checks_failed',ownership_check_required=False),
                                      dict(status='ready_for_review',ownership_check_required=False)),(1,1,1))
        self.assertEqual(e.read(self.root/'batch-status.json')['status'],'needs_attention')

    def test_blocked_stops_second_arm(self):
        self.assertEqual(self.run_case(dict(status='blocked',ownership_check_required=True),None),(1,0,0))

    def test_partial_stops_second_arm(self):
        self.assertEqual(self.run_case(dict(status='partial',ownership_check_required=False),None),(1,0,0))

    def test_solo_guard_rejects_other_model(self):
        with self.assertRaises(AssertionError):
            e.solo(dict(model='gpt-5.6-sol',effort='high',id='wrong'),self.root)


if __name__=='__main__': unittest.main()
