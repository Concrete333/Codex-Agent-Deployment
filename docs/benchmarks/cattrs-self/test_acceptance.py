"""Independent expectations for the Self migration; withheld from workers."""
import unittest
from dataclasses import dataclass
from typing import NamedTuple, Optional, TypedDict, Self

from attrs import define
from cattrs import Converter
from cattrs.cols import namedtuple_dict_structure_factory, namedtuple_dict_unstructure_factory


@define
class AttrNode:
    value: int
    child: Optional[Self]
    default_child: Optional[Self] = None


@define
class AttrChild(AttrNode):
    pass


@dataclass
class DataNode:
    value: int
    child: Optional[Self]


@dataclass
class DataChild(DataNode):
    pass


class DictNode(TypedDict):
    value: int
    child: Optional[Self]


class TupleNode(NamedTuple):
    value: int
    child: Optional[Self]


@define
class Mixed:
    first: AttrNode
    second: DataNode


class SelfChecks(unittest.TestCase):
    def converter(self):
        return Converter(detailed_validation=self.detailed)

    def test_attrs_recursive_defaults(self):
        c = self.converter()
        raw = {'value': '1', 'child': {'value': '2', 'child': None}}
        expected = AttrNode(1, AttrNode(2, None))
        self.assertEqual(c.structure(raw, AttrNode), expected)
        self.assertEqual(c.unstructure(expected), {
            'value': 1, 'child': {'value': 2, 'child': None, 'default_child': None}, 'default_child': None})

    def test_dataclass_recursive(self):
        c = self.converter()
        expected = DataNode(3, DataNode(4, None))
        self.assertEqual(c.structure({'value': '3', 'child': {'value': '4', 'child': None}}, DataNode), expected)
        self.assertEqual(c.unstructure(expected), {'value': 3, 'child': {'value': 4, 'child': None}})

    def test_attrs_subclass_binds_self(self):
        result = self.converter().structure({'value': 1, 'child': {'value': 2, 'child': None}}, AttrChild)
        self.assertIs(type(result), AttrChild)
        self.assertIs(type(result.child), AttrChild)

    def test_dataclass_subclass_binds_self(self):
        result = self.converter().structure({'value': 1, 'child': {'value': 2, 'child': None}}, DataChild)
        self.assertIs(type(result), DataChild)
        self.assertIs(type(result.child), DataChild)

    def test_typeddict_hooks_at_each_depth(self):
        c = self.converter()
        c.register_unstructure_hook(int, lambda v: f'n:{v}')
        c.register_structure_hook(int, lambda v, _: int(v.removeprefix('n:')))
        raw = {'value': 'n:1', 'child': {'value': 'n:2', 'child': None}}
        structured = {'value': 1, 'child': {'value': 2, 'child': None}}
        self.assertEqual(c.structure(raw, DictNode), structured)
        self.assertEqual(c.unstructure(structured, DictNode), raw)

    def test_namedtuple_dictionary_factories(self):
        c = self.converter()
        c.register_structure_hook_factory(lambda t: t is TupleNode, namedtuple_dict_structure_factory)
        c.register_unstructure_hook_factory(lambda t: t is TupleNode, namedtuple_dict_unstructure_factory)
        expected = TupleNode(1, TupleNode(2, None))
        self.assertEqual(c.structure({'value': '1', 'child': {'value': '2', 'child': None}}, TupleNode), expected)
        self.assertEqual(c.unstructure(expected), {'value': 1, 'child': {'value': 2, 'child': None}})

    def test_multiple_self_classes_in_one_graph(self):
        c = self.converter()
        expected = Mixed(AttrNode(1, AttrNode(2, None)), DataNode(3, DataNode(4, None)))
        raw = {'first': {'value': 1, 'child': {'value': 2, 'child': None, 'default_child': None}, 'default_child': None},
               'second': {'value': 3, 'child': {'value': 4, 'child': None}}}
        self.assertEqual(c.structure(raw, Mixed), expected)
        self.assertEqual(c.unstructure(expected), raw)

    def test_converter_isolation(self):
        first, second = self.converter(), self.converter()
        first.register_unstructure_hook(int, str)
        expected = DataNode(1, DataNode(2, None))
        self.assertEqual(first.unstructure(expected), {'value': '1', 'child': {'value': '2', 'child': None}})
        self.assertEqual(second.unstructure(expected), {'value': 1, 'child': {'value': 2, 'child': None}})


def suite():
    result = unittest.TestSuite()
    for detailed in (False, True):
        case = type('Detailed' if detailed else 'Simple', (SelfChecks,), {'detailed': detailed})
        result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    return result


if __name__ == '__main__':
    outcome = unittest.TextTestRunner(verbosity=2).run(suite())
    raise SystemExit(not outcome.wasSuccessful())
