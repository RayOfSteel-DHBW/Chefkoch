import unittest
from unittest import result
from ContentParser import ContentParser
from ChefkochDataService import CategoryModel, RecipeModel

class TestContentParser(unittest.TestCase):
    def setUp(self):
        self.parser = ContentParser()

    def test_get_params_from_url_recipe(self):
        # Test recipe URL
        url="https://www.chefkoch.de/rezepte/1234567/Recipe-Name.html"
        params = self.parser.get_params_from_url(url)
        self.assertEqual(params, {"1234567": "Recipe-Name"})

    def test_get_params_from_url_category(self):
        # Test category URL with rs path
        url="https://www.chefkoch.de/rs/s0t42/Category-Name.html"
        params = self.parser.get_params_from_url(url)
        self.assertEqual(params, {"s": "0", "t": "42"})

    def test_get_params_from_url_complex_category(self):
        # Test category URL with multiple parameters
        url="https://www.chefkoch.de/rs/s0g34e5t42/Complex-Category.html"
        params = self.parser.get_params_from_url(url)
        compare = {"s": "0", "g": "34", "e": "5", "t": "42"}
        self.assertDictEqual(params, compare)

if __name__ == '__main__':
    TestContentParser().test_get_params_from_url_complex_category()
    unittest.main()