"""Offline configuration checks; no provider calls."""
import json
import unittest

import external_workers as experiment


class Catalog(unittest.TestCase):
    def catalog(self, overrides=None):
        rows = []
        for name, (model, variant) in experiment.WORKERS.items():
            item = {'variants': {variant: {'reasoning': {'enabled': True,
                    'effort': 'high' if name == 'mimo' else 'max'}}}, 'limit': {'output': 131072}}
            if overrides and name in overrides:
                item.update(overrides[name])
            rows.append(model + '\n' + json.dumps(item))
        return '\n'.join(rows)

    def test_exact_requested_variants(self):
        self.assertEqual(set(experiment.selected_catalog(self.catalog())), set(experiment.WORKERS))

    def test_refuses_missing_or_weaker_variant(self):
        with self.assertRaises(ValueError):
            experiment.selected_catalog(self.catalog({'deepseek': {'variants': {'high': {}}}}))

    def test_refuses_insufficient_output_allowance(self):
        with self.assertRaises(ValueError):
            experiment.selected_catalog(self.catalog({'glm': {'limit': {'output': 32000}}}))


if __name__ == '__main__':
    unittest.main()
