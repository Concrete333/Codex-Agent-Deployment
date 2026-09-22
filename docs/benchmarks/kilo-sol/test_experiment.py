"""Offline regression for CLI event framing; no models or provider calls."""
import json
from pathlib import Path
import tempfile
import unittest

from experiment import jsonl_events


class EventFraming(unittest.TestCase):
    def test_unicode_separator_inside_json_string(self):
        events = [{'text': 'before\u2028middle\u2029after'}, {'type': 'turn.completed'}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            path.write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in events), encoding='utf-8')
            self.assertEqual(jsonl_events(path), events)

    def test_malformed_record_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            path.write_text('{"text":"incomplete', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                jsonl_events(path)


if __name__ == '__main__':
    unittest.main()
