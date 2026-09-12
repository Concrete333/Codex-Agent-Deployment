"""Offline tests of spending bounds and failure feedback; never invoke a model."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiment


class DriverTests(unittest.TestCase):
    def exercise(self,statuses):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); state=root/'state'; state.mkdir()
            pointer=root/'pointer.json'
            pointer.write_text(json.dumps({'root':str(root)}),encoding='utf-8')
            manifest={'state':str(state),'identity':'fixture','order':['B','A'],'frozen':{}}
            (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            def job_for(root,identity,arm,number=0):
                return {'id':f'{identity}-{arm}-{number}','model':'gpt-5.6-sol' if number else 'gpt-5.6-luna',
                        'effort':'high' if number else 'max','prompt':f'Frozen arm {arm}\n'}
            for arm in manifest['order']:
                (root/arm).mkdir()
                (root/arm/'request.json').write_text(json.dumps(job_for(root,'fixture',arm)),encoding='utf-8')
            calls=[]
            def execute(job,state,binary):
                calls.append(copy.deepcopy(job))
                status=statuses[len(calls)-1]
                folder=state/job['id']; folder.mkdir()
                log=folder/'check.stdout'; log.write_text('EXACT failure: expected 5; got 3\n',encoding='utf-8')
                (folder/'receipt.json').write_text(json.dumps({'checks':[{'stdout_path':str(log)}]}),encoding='utf-8')
                return {'status':status,'ownership_check_required':False}
            with patch.object(experiment,'POINTER',pointer),patch.object(experiment,'job_for',side_effect=job_for),\
                 patch.object(experiment.runner,'run',side_effect=execute),patch.object(experiment,'summarize'),\
                 contextlib.redirect_stdout(io.StringIO()):
                experiment.run()
                with self.assertRaises(FileExistsError): experiment.run()
            return calls

    def test_clean_pair_never_launches_repair(self):
        calls=self.exercise(['ready_for_review','ready_for_review'])
        self.assertEqual([j['model'] for j in calls],['gpt-5.6-luna']*2)

    def test_each_failed_arm_has_one_sol_correction_and_exact_feedback(self):
        calls=self.exercise(['checks_failed','checks_failed','checks_failed','checks_failed'])
        self.assertEqual([j['model'] for j in calls],['gpt-5.6-luna','gpt-5.6-sol']*2)
        self.assertTrue(all('EXACT failure: expected 5; got 3\n' in calls[i]['prompt'] for i in [1,3]))
        self.assertEqual([j['effort'] for j in calls],['max','high']*2)

    def test_blocked_stops_without_successor(self):
        self.assertEqual(len(self.exercise(['blocked'])),1)

    def test_partial_has_no_automatic_correction(self):
        calls=self.exercise(['partial','ready_for_review'])
        self.assertEqual([j['model'] for j in calls],['gpt-5.6-luna']*2)


if __name__=='__main__': unittest.main()
