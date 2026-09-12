"""Independent acceptance and integrity checks. Outside worker scope."""
import argparse
import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import random
import sys
import unittest

TARGET = None


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.stock = {('a', 'x'): 10, ('a', 'y'): 7, ('b', 'x'): 90, ('a', ' x '): 8}

    def test_duplicate_first_order_and_tenant(self):
        rows = reserve(self.stock, 'a', [dict(sku=s, quantity=n) for s,n in [('y',2),('x',3),('y',1)]])
        self.assertEqual(rows, [dict(sku='y', quantity=3, remaining=4), dict(sku='x', quantity=3, remaining=7)])
        self.assertEqual(self.stock, {('a','x'):7, ('a','y'):4, ('b','x'):90, ('a',' x '):8})

    def test_identities_not_normalized(self):
        for tenant, sku in [(' A ', 'x'), ('a','X'), (' ', ' ')]:
            stock = {(tenant,sku):4, ('a','x'):10}
            self.assertEqual(reserve(stock, tenant, [dict(sku=sku,quantity=2)]), [dict(sku=sku,quantity=2,remaining=2)])
            self.assertEqual(stock[('a','x')],10)

    def test_rollback_after_valid_lines(self):
        for tail in [dict(sku='missing',quantity=1), dict(sku='y',quantity=99),
                     dict(sku='x',quantity=True), dict(sku='',quantity=1),
                     dict(sku='y',quantity=0), dict(sku='y',quantity=1,extra=1),
                     {}, {'sku':'y'}, {'quantity':1}, None, []]:
            for dry in [False,True]:
                with self.subTest(tail=tail,dry=dry):
                    stock=copy.deepcopy(self.stock)
                    with self.assertRaises(ValueError):
                        reserve(stock,'a',[dict(sku='x',quantity=2),tail],dry_run=dry)
                    self.assertEqual(stock,self.stock)

    def test_duplicate_overdraw_is_atomic(self):
        with self.assertRaises(ValueError):
            reserve(self.stock,'a',[dict(sku='x',quantity=6),dict(sku='x',quantity=5)])
        self.assertEqual(self.stock[('a','x')],10)

    def test_invalid_values(self):
        class Text(str): pass
        class Count(int): pass
        class Row(dict): pass
        for tenant in ['',None,1,Text('a')]:
            with self.subTest(tenant=repr(tenant)), self.assertRaises(ValueError):
                reserve(self.stock,tenant,[])
        for flag in [None,0,1,'false']:
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                reserve(self.stock,'a',[],dry_run=flag)
        for sku in ['',None,3,Text('x')]:
            with self.subTest(sku=repr(sku)), self.assertRaises(ValueError):
                reserve(self.stock,'a',[dict(sku=sku,quantity=1)])
        for quantity in [True,False,0,-1,1.0,'1',None,Count(1)]:
            with self.subTest(quantity=repr(quantity)), self.assertRaises(ValueError):
                reserve(self.stock,'a',[dict(sku='x',quantity=quantity)])
        for lines in [None,3,False]:
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                reserve(self.stock,'a',lines)
        with self.assertRaises(ValueError):
            reserve(self.stock,'a',[Row(sku='x',quantity=1)])

    def test_generator_and_input_unchanged(self):
        lines=[dict(sku='x',quantity=2),dict(sku='x',quantity=3)]
        original=copy.deepcopy(lines)
        rows=reserve(self.stock,'a',(r for r in lines))
        self.assertEqual(rows,[dict(sku='x',quantity=5,remaining=5)])
        rows[0]['quantity']=999
        self.assertEqual(lines,original)
        self.assertEqual(self.stock[('a','x')],5)

    def test_iterator_failure_propagates_without_write(self):
        for error in [RuntimeError('iterator sentinel'),TypeError('iterator sentinel')]:
            def broken():
                yield dict(sku='x',quantity=2)
                raise error
            try:
                reserve(self.stock,'a',broken())
            except Exception as observed:
                self.assertIs(observed,error)
            else:
                self.fail('iterator exception swallowed')
            self.assertEqual(self.stock[('a','x')],10)

    def test_empty_and_preview(self):
        before=copy.deepcopy(self.stock)
        self.assertEqual(reserve(self.stock,'a',[]),[])
        self.assertEqual(reserve(self.stock,'a',[dict(sku='x',quantity=10)],dry_run=True),
                         [dict(sku='x',quantity=10,remaining=0)])
        self.assertEqual(self.stock,before)

    def test_service_journal_isolation(self):
        journal=[{'old':True}]
        service=Service(self.stock,journal)
        result=service.submit('a',[dict(sku='x',quantity=3)])
        self.assertEqual(journal,[{'old':True},{'tenant':'a','reserved':[dict(sku='x',quantity=3,remaining=7)]}])
        result['reserved'][0]['remaining']=-90
        result['reserved'].append({})
        self.assertEqual(journal[1]['reserved'],[dict(sku='x',quantity=3,remaining=7)])
        self.assertEqual(self.stock[('a','x')],7)
        self.assertEqual(service.submit('a',[]),{'reserved':[]})
        self.assertEqual(journal[-1],{'tenant':'a','reserved':[]})

    def test_service_preview_and_failures(self):
        journal=[]
        service=Service(self.stock,journal)
        before=copy.deepcopy(self.stock)
        self.assertEqual(service.preview('a',[dict(sku='x',quantity=2)]),{'reserved':[dict(sku='x',quantity=2,remaining=8)]})
        for method in [service.submit,service.preview]:
            with self.assertRaises(ValueError):
                method('a',[dict(sku='y',quantity=1),dict(sku='x',quantity=99)])
        self.assertEqual((self.stock,journal),(before,[]))

    def test_api_dispatch_without_reimplementation(self):
        class Request(dict): pass
        class Spy:
            def __init__(self): self.calls=[]; self.result=object()
            def submit(self,*args): self.calls.append(('commit',args)); return self.result
            def preview(self,*args): self.calls.append(('preview',args)); return self.result
        for mode in [None,'commit','preview']:
            spy=Spy(); lines=iter([]); request={'tenant':'a','lines':lines}
            if mode is not None: request['mode']=mode
            self.assertIs(handle(spy,request),spy.result)
            self.assertEqual(spy.calls,[(mode or 'commit',('a',lines))])
        for request in [None,[],{}, Request(tenant='a',lines=[]), {'tenant':'a'}, {'tenant':'a','lines':[],'extra':1},
                        {'tenant':'a','lines':[],'mode':'PREVIEW'}, {'tenant':'a','lines':[],'mode':None},
                        {'tenant':'a','lines':[],'mode':[]}]:
            spy=Spy()
            with self.subTest(request=request),self.assertRaises(ValueError): handle(spy,request)
            self.assertEqual(spy.calls,[])

    def test_fixed_seed_batch_sequences(self):
        rng=random.Random(2026091207)
        stock={(t,s):rng.randrange(1,25) for t in ['a','b'] for s in ['x','y','z']}
        expected=copy.deepcopy(stock)
        journal=[]; service=Service(stock,journal); expected_journal=[]
        for turn in range(100):
            tenant=rng.choice(['a','b']); mode=rng.choice(['commit','preview'])
            lines=[dict(sku=rng.choice(['x','y','z','missing']),quantity=rng.randrange(1,8)) for _ in range(rng.randrange(5))]
            distinct=list(dict.fromkeys(row['sku'] for row in lines))
            totals={sku:sum(row['quantity'] for row in lines if row['sku']==sku) for sku in distinct}
            valid=all(n<=expected.get((tenant,sku),0) for sku,n in totals.items())
            with self.subTest(turn=turn):
                if valid:
                    rows=[dict(sku=sku,quantity=totals[sku],remaining=expected.get((tenant,sku),0)-totals[sku]) for sku in distinct]
                    self.assertEqual(handle(service,dict(tenant=tenant,lines=lines,mode=mode)),{'reserved':rows})
                    if mode=='commit':
                        for row in rows: expected[(tenant,row['sku'])]=row['remaining']
                        expected_journal.append({'tenant':tenant,'reserved':copy.deepcopy(rows)})
                else:
                    with self.assertRaises(ValueError): handle(service,dict(tenant=tenant,lines=lines,mode=mode))
                self.assertEqual(stock,expected)
                self.assertEqual(journal,expected_journal)


def main():
    global TARGET, reserve, Service, handle, core, service_module
    parser=argparse.ArgumentParser()
    parser.add_argument('target',type=Path)
    parser.add_argument('--protected',type=Path,required=True)
    args=parser.parse_args(); TARGET=args.target.resolve()
    protected=json.loads(args.protected.read_text(encoding='utf-8'))
    changes=[p for p,h in protected.items() if not (TARGET/p).is_file() or hashlib.sha256((TARGET/p).read_bytes()).hexdigest()!=h]
    if changes:
        print(json.dumps({'accepted':False,'integrity_failures':changes})); return 1
    sys.path.insert(0,str(TARGET))
    core=importlib.import_module('reservation.core'); service_module=importlib.import_module('reservation.service')
    reserve=core.reserve_batch; Service=service_module.ReservationService
    handle=importlib.import_module('reservation.api').handle
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests)
    suite.addTests(unittest.defaultTestLoader.discover(str(TARGET/'tests'),pattern='test_public.py'))
    stream=io.StringIO(); result=unittest.TextTestRunner(stream=stream,verbosity=0).run(suite)
    print(json.dumps({'accepted':result.wasSuccessful(),'test_methods':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'details':stream.getvalue(),
        'structural_review_required':'Verify preview calls the shared core with dry_run=True; inspect changed source and added tests.'}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__': raise SystemExit(main())
