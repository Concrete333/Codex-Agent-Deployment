"""Offline result validation and dispatch bounds; no models."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import acceptance_pair as a


class ReviewBounds(unittest.TestCase):
    def report(self,**changes):
        return dict(status='complete',decision='accept',summary='Reviewed',coverage=['SPEC.md'],findings=[],uncertainties=[],**changes)

    def test_valid_accept(self):
        self.assertEqual(a.validate_report(self.report(),['SPEC.md'])['decision'],'accept')

    def test_accept_needs_coverage(self):
        with self.assertRaises(ValueError): a.validate_report(self.report(),['SPEC.md','inventory/api.py'])

    def test_reject_needs_finding(self):
        value=self.report(); value['decision']='reject'
        with self.assertRaises(ValueError): a.validate_report(value,['SPEC.md'])

    def test_partial_cannot_accept(self):
        value=self.report(); value['status']='partial'
        with self.assertRaises(ValueError): a.validate_report(value,['SPEC.md'])

    def test_coverage_normalizes_relative_paths(self):
        value=self.report(); value['coverage']=['./SPEC.md','inventory\\api.py']
        a.validate_report(value,['SPEC.md','inventory/api.py'])

    def dispatch(self,result):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); pointer=root/'pointer.json'
            a.save(pointer,dict(root=str(root)))
            a.save(root/'manifest.json',dict(frozen={},state=str(root/'state'),cases=[{'label':'case-1'},{'label':'case-2'}]))
            with patch.object(a,'POINTER',pointer),patch.object(a,'review',return_value=result) as review,patch.object(a,'summarize'):
                if result['status']!='completed':
                    with self.assertRaises(RuntimeError): a.run()
                    self.assertEqual(review.call_count,1)
                else:
                    a.run(); self.assertEqual(review.call_count,2)
                    with self.assertRaises(FileExistsError): a.run()
                    self.assertEqual(review.call_count,2)

    def test_exactly_two_attempts_and_no_repeat(self): self.dispatch(dict(status='completed'))
    def test_partial_stops_before_second(self): self.dispatch(dict(status='needs_attention'))


if __name__=='__main__': unittest.main()
