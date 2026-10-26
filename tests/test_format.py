import unittest

from mybestsim.format import format_fr


class FormatFrTest(unittest.TestCase):
    def test_entier(self):
        self.assertEqual(format_fr(5056), "5 056")

    def test_decimales(self):
        self.assertEqual(format_fr(14.49, 2), "14,49")


if __name__ == "__main__":
    unittest.main()
