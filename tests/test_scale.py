import unittest
from types import SimpleNamespace

from mcd_client import extract_food_names
from scale import Dimensions, convert


class ScaleTests(unittest.TestCase):
    def test_length_and_bounding_volume(self):
        actual = convert(Dimensions(120, 60, 75), Dimensions(10, 5, 5))
        self.assertEqual(actual, {"length": 12, "width": 12, "area": 144, "height": 15, "volume": 2160})

    def test_rejects_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            Dimensions(0)
        with self.assertRaises(ValueError):
            Dimensions(10, None, 4)

    def test_extracts_structured_and_text_results(self):
        result = SimpleNamespace(
            structured_content={"data": [{"foodName": "巨无霸"}]},
            content=[SimpleNamespace(text='{"items":[{"product_name":"薯条"}]}')],
        )
        self.assertEqual(extract_food_names(result), ["巨无霸", "薯条"])

    def test_extracts_documented_toon_payload(self):
        toon = "[2]{productName,nutritionDescription,energyKj}:\n  猪柳麦满分,null,1288\n  巨无霸,null,2000\n"
        result = SimpleNamespace(structured_content={"data": toon}, content=[])
        self.assertEqual(extract_food_names(result), ["巨无霸", "猪柳麦满分"])


if __name__ == "__main__":
    unittest.main()
