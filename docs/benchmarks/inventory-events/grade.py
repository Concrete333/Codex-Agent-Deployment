"""Independent, literal-outcome acceptance checks. No participant imports before integrity checks."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest


def event(kind='receive', identity='r', tenant='a', quantity=1, **extra):
    return dict(kind=kind, event_id=identity, tenant=tenant, quantity=quantity, **extra)


class HiddenTests(unittest.TestCase):
    def test_initial_validation(self):
        class Text(str): pass
        class Count(int): pass
        class Pair(tuple): pass
        class Mapping(dict): pass
        for initial in [None, [], Mapping(), {('a',): 1}, {'ax': 1},
                        {Pair(('a','x')): 1}, {('', 'x'): 1}, {(Text('a'),'x'): 1},
                        {('a','x'): -1}, {('a','x'): True}, {('a','x'): Count(2)}, {('a','x'): 1.0}]:
            with self.subTest(initial=repr(initial)), self.assertRaises(ValueError): Ledger(initial)

    def test_validation_atomic_and_sequence(self):
        class Text(str): pass
        class Count(int): pass
        class Mapping(dict): pass
        good = event(sku='x')
        invalid = [None, [], {}, Mapping(good), dict(good, kind=Text('receive')),
                   dict(good, kind=[]), dict(good, kind='other'), dict(good, extra=1)]
        invalid += [{k:v for k,v in good.items() if k != missing} for missing in good]
        invalid += [dict(good, **{field:value}) for field in ['event_id','tenant','sku']
                    for value in ['', None, 2, Text('a')]]
        invalid += [dict(good, quantity=v) for v in [True,False,0,-1,1.0,'1',Count(1)]]
        invalid += [event('transfer', to_tenant=v, sku='x') for v in ['',None,Text('b'),'a']]
        invalid += [event('hold', sku='x', hold_id=v) for v in ['',None,Text('h')]]
        for tail in invalid:
            ledger = Ledger({('a','x'): 20})
            before = ledger.snapshot()
            with self.subTest(tail=repr(tail)), self.assertRaises(ValueError):
                ledger.apply([event(identity='valid',sku='x'), tail])
            self.assertEqual(ledger.snapshot(), before)
            self.assertEqual(ledger.apply([event(identity='valid',sku='x')])[0]['sequence'], 1)

    def test_available_uses_all_holds_and_tenants(self):
        ledger = Ledger({('a','x'):10, ('b','x'):100, ('a','y'):20})
        ledger.apply([event('hold','h1',quantity=4,sku='x',hold_id='1'),
                      event('hold','h2',quantity=3,sku='x',hold_id='2'),
                      event('hold','h3',quantity=8,sku='y',hold_id='3')])
        before = ledger.snapshot()
        for e in [event('hold','h4',quantity=4,sku='x',hold_id='4'),
                  event('transfer','t',quantity=4,sku='x',to_tenant='b')]:
            with self.assertRaises(ValueError): ledger.apply([e])
            self.assertEqual(ledger.snapshot(), before)
        ledger.apply([event('transfer','t',quantity=3,sku='x',to_tenant='b')])
        self.assertEqual(ledger.snapshot()['stock'], [
            dict(tenant='a',sku='x',on_hand=7,held=7,available=0),
            dict(tenant='a',sku='y',on_hand=20,held=8,available=12),
            dict(tenant='b',sku='x',on_hand=103,held=0,available=103)])

    def test_hold_lifecycle(self):
        ledger = Ledger({('a','x'):9, ('a','y'):4, ('b','x'):2})
        ledger.apply([event('hold','h',quantity=7,sku='x',hold_id='same')])
        before = ledger.snapshot()
        for e in [event('hold','h2',sku='y',hold_id='same'),
                  event('release','r',quantity=8,hold_id='same'),
                  event('ship','s',tenant='b',hold_id='same'),
                  event('release','r',hold_id='missing')]:
            with self.assertRaises(ValueError): ledger.apply([e])
            self.assertEqual(ledger.snapshot(), before)
        ledger.apply([event('release','r',quantity=2,hold_id='same'),
                      event('ship','s',quantity=3,hold_id='same')])
        self.assertEqual(ledger.snapshot()['holds'], [dict(tenant='a',hold_id='same',sku='x',quantity=2)])
        self.assertEqual(ledger.snapshot()['stock'][0], dict(tenant='a',sku='x',on_hand=6,held=2,available=4))
        ledger.apply([event('release','r2',quantity=2,hold_id='same'),
                      event('hold','h2',sku='y',hold_id='same')])
        self.assertEqual(ledger.snapshot()['holds'], [dict(tenant='a',hold_id='same',sku='y',quantity=1)])

    def test_transfer_missing_and_zero(self):
        ledger = Ledger({('a','x'):3})
        for e in [event('transfer','t',sku='missing',to_tenant='b'),
                  event('hold','h',sku='missing',hold_id='h')]:
            with self.assertRaises(ValueError): ledger.apply([e])
            self.assertEqual(len(ledger.snapshot()['stock']),1)
        ledger.apply([event('transfer','t',quantity=3,sku='x',to_tenant='b')])
        self.assertEqual(ledger.snapshot()['stock'], [dict(tenant='a',sku='x',on_hand=0,held=0,available=0),
                                                    dict(tenant='b',sku='x',on_hand=3,held=0,available=3)])

    def test_replay_global_conflict_and_rollback(self):
        ledger = Ledger({})
        original = event(sku='x',quantity=5)
        ledger.apply([original])
        before = ledger.snapshot()
        for conflict in [dict(original, tenant='b'),dict(original,quantity=6),dict(original,sku='y')]:
            with self.assertRaises(ValueError): ledger.apply([event(identity='new',sku='y'),conflict])
            self.assertEqual(ledger.snapshot(),before)
        receipt = ledger.apply([dict(reversed(list(original.items()))),event(identity='new',sku='y')])
        self.assertEqual(receipt, [dict(event_id='r',kind='receive',sequence=1,replayed=True),
                                   dict(event_id='new',kind='receive',sequence=2,replayed=False)])

    def test_same_batch_replay_and_conflict(self):
        original = event(sku='x',quantity=5)
        ledger = Ledger({})
        with self.assertRaises(ValueError): ledger.apply([original,dict(original,quantity=6)])
        self.assertEqual(ledger.snapshot(),dict(stock=[],holds=[],event_count=0))
        receipts = ledger.apply([original,dict(original),event('hold','h',sku='x',hold_id='h',quantity=5)])
        self.assertEqual([r['sequence'] for r in receipts],[1,1,2])
        self.assertEqual(ledger.snapshot()['stock'][0]['on_hand'],5)

    def test_copy_isolation(self):
        initial = {('a','x'):10}
        ledger = Ledger(initial)
        initial[('a','x')] = 500
        e = event('hold','h',sku='x',hold_id='h',quantity=3)
        original = dict(e)
        receipt = ledger.apply([e])
        expected = copy.deepcopy(ledger.snapshot())
        e['quantity'] = 8
        receipt[0]['sequence'] = 999
        snap = ledger.snapshot()
        snap['stock'][0]['on_hand'] = 1
        snap['holds'][0]['quantity'] = 8
        self.assertEqual(ledger.snapshot(),expected)
        self.assertEqual(ledger.apply([original])[0],dict(event_id='h',kind='hold',sequence=1,replayed=True))
        replay = ledger.apply([original])
        replay[0]['sequence'] = 1234
        replay[0]['kind'] = 'ship'
        self.assertEqual(ledger.apply([original])[0],dict(event_id='h',kind='hold',sequence=1,replayed=True))

    def test_iterator_and_preview_rollback(self):
        for dry in [False, True]:
            for failure in [TypeError('sentinel'),RuntimeError('sentinel')]:
                ledger = Ledger({})
                def broken():
                    yield event(sku='x', quantity=5)
                    raise failure
                with self.assertRaises(type(failure)) as raised: ledger.apply(broken(),dry_run=dry)
                self.assertIs(raised.exception,failure)
                self.assertEqual(ledger.snapshot(),dict(stock=[],holds=[],event_count=0))
                self.assertEqual(ledger.apply([event(sku='x')])[0],
                                 dict(event_id='r',kind='receive',sequence=1,replayed=False))

    def test_all_state_rollback_after_operation_prefix(self):
        for prefix in [event('hold','p',sku='x',hold_id='other'),
                       event('release','p',hold_id='h'),event('ship','p',hold_id='h'),
                       event('transfer','p',sku='x',to_tenant='b')]:
            ledger = Ledger({('a','x'):10})
            ledger.apply([event('hold','seed',sku='x',hold_id='h',quantity=5)])
            before = ledger.snapshot()
            with self.assertRaises(ValueError): ledger.apply([prefix,{}])
            self.assertEqual(ledger.snapshot(),before)
            self.assertEqual(ledger.apply([prefix])[0]['sequence'],2)

    def test_preview_rejects_invalid_and_conflicting_events(self):
        ledger = Ledger({('a','x'):10})
        original = event(sku='x')
        ledger.apply([original])
        before = ledger.snapshot()
        for tail in [{}, dict(original,quantity=2),event('hold','bad',sku='x',hold_id='h',quantity=99),
                     event('ship','bad',hold_id='missing')]:
            with self.assertRaises(ValueError): ledger.preview([event(identity='new',sku='y'),tail])
            self.assertEqual(ledger.snapshot(),before)
        self.assertEqual(ledger.apply([event(identity='new',sku='y')])[0]['sequence'],2)

    def test_replay_compares_kind_and_specific_fields(self):
        pairs = [(event('transfer','t',sku='x',to_tenant='b'),event('transfer','t',sku='x',to_tenant='c')),
                 (event('hold','h',sku='x',hold_id='one'),event('hold','h',sku='x',hold_id='two')),
                 (event('release','r',hold_id='seed'),event('ship','r',hold_id='seed'))]
        for first,second in pairs:
            ledger = Ledger({('a','x'):10})
            ledger.apply([event('hold','seed',sku='x',hold_id='seed',quantity=3),first])
            before = ledger.snapshot()
            with self.assertRaises(ValueError): ledger.apply([second])
            self.assertEqual(ledger.snapshot(),before)

    def test_preview_equivalent_and_uncommitted_ids(self):
        ledger = Ledger({('a','x'):10})
        existing = event('hold','h',sku='x',hold_id='h',quantity=5)
        ledger.apply([existing])
        events = [existing,event('ship','s',hold_id='h',quantity=3),event('transfer','t',sku='x',to_tenant='b',quantity=5)]
        before = ledger.snapshot()
        expected = [dict(event_id='h',kind='hold',sequence=1,replayed=True),
                    dict(event_id='s',kind='ship',sequence=2,replayed=False),
                    dict(event_id='t',kind='transfer',sequence=3,replayed=False)]
        self.assertEqual(ledger.preview(e for e in events),expected)
        self.assertEqual(ledger.snapshot(),before)
        self.assertEqual(ledger.apply(events),expected)

    def test_exact_identity_order_and_huge_ints(self):
        huge = 10**400
        ledger = Ledger({('z','x'):huge, (' A ',' '):1, ('a','X'):2, ('a','x'):3})
        ledger.apply([event('transfer',' t ',tenant='z',quantity=huge,sku='x',to_tenant=' '),
                      event('hold','h1',tenant='a',sku='x',hold_id='z'),
                      event('hold','h2',tenant='a',sku='X',hold_id=' a ')])
        snap = ledger.snapshot()
        self.assertEqual([(r['tenant'],r['sku']) for r in snap['stock']], [(' ','x'),(' A ',' '),('a','X'),('a','x'),('z','x')])
        self.assertEqual(snap['stock'][0]['on_hand'],huge)
        self.assertEqual([r['hold_id'] for r in snap['holds']],[' a ','z'])

    def test_empty_and_argument_types(self):
        ledger = Ledger({})
        for invalid in [None,3,False]:
            with self.assertRaises(ValueError): ledger.apply(invalid)
        for flag in [None,0,1,'false']:
            with self.assertRaises(ValueError): ledger.apply([],dry_run=flag)
        self.assertEqual(ledger.preview(iter([])),[])
        self.assertEqual(ledger.apply([]),[])
        self.assertEqual(ledger.snapshot(),dict(stock=[],holds=[],event_count=0))

    def test_api(self):
        class Mapping(dict): pass
        class Text(str): pass
        class Spy:
            def __init__(self): self.calls=[]; self.result=object()
            def apply(self,events): self.calls.append(('commit',events)); return self.result
            def preview(self,events): self.calls.append(('preview',events)); return self.result
        for request in [None,[],{},Mapping(events=[]),dict(events=[],extra=1),
                        dict(events=[],mode=[]),dict(events=[],mode=None),dict(events=[],mode=Text('commit'))]:
            spy=Spy()
            with self.assertRaises(ValueError): handle(spy,request)
            self.assertEqual(spy.calls,[])
        for mode in [None,'commit','preview']:
            spy=Spy(); events=iter([]); request=dict(events=events)
            if mode is not None: request['mode']=mode
            self.assertIs(handle(spy,request),spy.result)
            self.assertEqual(spy.calls,[(mode or 'commit',events)])

    def test_long_sequence_literal_totals(self):
        ledger = Ledger({('a','x'):1000})
        events = []
        for i in range(150):
            events += [event('hold',f'h{i}',sku='x',hold_id=f'h{i}',quantity=3),
                       event('release',f'r{i}',hold_id=f'h{i}'),
                       event('ship',f's{i}',hold_id=f'h{i}',quantity=2)]
        rows = ledger.apply(e for e in events)
        self.assertEqual([r['sequence'] for r in rows], list(range(1,451)))
        expected = dict(stock=[dict(tenant='a',sku='x',on_hand=700,held=0,available=700)],holds=[],event_count=450)
        self.assertEqual(ledger.snapshot(),expected)
        self.assertTrue(all(r['replayed'] for r in ledger.apply(events)))
        self.assertEqual(ledger.snapshot(),expected)


def main():
    global Ledger, handle
    p=argparse.ArgumentParser(); p.add_argument('target',type=Path); p.add_argument('--protected',type=Path,required=True)
    args=p.parse_args(); target=args.target.resolve()
    protected=json.loads(args.protected.read_text())
    bad=[name for name,sha in protected.items() if not (target/name).is_file() or hashlib.sha256((target/name).read_bytes()).hexdigest()!=sha]
    if bad:
        print(json.dumps({'passed':False,'integrity_failures':bad})); return 1
    sys.path.insert(0,str(target))
    from inventory import Ledger, handle
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(HiddenTests)
    suite.addTests(unittest.defaultTestLoader.discover(str(target/'tests'),pattern='test_public.py'))
    out=io.StringIO(); result=unittest.TextTestRunner(stream=out,verbosity=0).run(suite)
    print(json.dumps({'passed':result.wasSuccessful(),'methods':result.testsRun,'failures':len(result.failures),
                      'errors':len(result.errors),'details':out.getvalue(),'source_review_required':True}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__': raise SystemExit(main())
