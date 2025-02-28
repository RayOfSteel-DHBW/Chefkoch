import unittest
import os
from Crawler.ChefkochDataService import CategoryModel, RecipeModel
from Crawler.ContentParser import ContentParser
from Crawler.ParsingResult import ParsingResult

class TestContentParser(unittest.TestCase):
    def setUp(self):
        self.parser = ContentParser()

    def loadFile(self, fileName) -> str:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'Data', f'{fileName}.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
        return self.html_content  
    
    def test_parse_with_html_content(self):
        # Load test HTML file
        self.loadFile('testFile')
        # Test parsing the actual HTML content
        result = self.parser.parse(self.html_content, is_recipe=False)
        
        # Verify the category URL was found
        self.assertIn("https://www.chefkoch.de/rs/s0o6/Rezepte.html", result.foundRecipes)
    
    def test_parse_recipe_in_html(self):
        # Load recipe test HTML file
        self.loadFile('recipe-test')
        # Test parsing for recipe URLs
        result = self.parser.parse(self.html_content, is_Rrecipe=True)
        assert isinstance(result, ParsingResult)
        assert isinstance(result.entity, RecipeModel)
        assert(result.entity.name == "Das beste Kartoffelgratin")
        assert(result.entity.url == "https://www.chefkoch.de/rezepte/644981165672475/Das-beste-Kartoffelgratin.html")
    
    def test_parse_empty_content(self):
        # Test with empty content
        result = self.parser.parse("", is_recipe=False)
        
        # Verify the result
        self.assertIsInstance(result, ParsingResult)
        self.assertIsInstance(result.entity, CategoryModel)
        self.assertEqual(result.entity.name, "")
        self.assertEqual(result.entity.url, "")

if __name__ == '__main__':
    unittest.main()