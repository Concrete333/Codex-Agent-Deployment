import unittest
from labels import normalize_labels


class LabelContract(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(normalize_labels([]), [])

    def test_normalization_and_order(self):
        self.assertEqual(normalize_labels([" Blue ", "RED", "blue", "Green", " red "]), ["blue", "red", "green"])

    def test_empty_values(self):
        self.assertEqual(normalize_labels(["", " \t\n", "kept", "\u2003"]), ["kept"])

    def test_unicode_casefold(self):
        self.assertEqual(normalize_labels(["Straße", "STRASSE", "Σ", "ς"]), ["strasse", "σ"])

    def test_preserve_internal_text(self):
        self.assertEqual(normalize_labels([" A  B ", "a-b", "a  b", " X/Y! "]), ["a  b", "a-b", "x/y!"])

    def test_input_unchanged_and_new_result(self):
        values = [" Blue ", "blue", "RED"]
        original = values[:]
        result = normalize_labels(values)
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_non_list(self):
        for value in (None, "abc", ("abc",), {"abc"}, {}, 7, True):
            with self.subTest(value=value), self.assertRaises(TypeError):
                normalize_labels(value)

    def test_non_string_element(self):
        for value in (None, 3, False, [], b"a"):
            with self.subTest(value=value), self.assertRaises(TypeError):
                normalize_labels(["ok", value])

    def test_all_duplicate(self):
        self.assertEqual(normalize_labels(["a", "A", " a "]), ["a"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
