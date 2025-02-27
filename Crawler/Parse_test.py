import unittest
import os
from Crawler.ContentParser import ContentParser
from Crawler.ParsingResult import ParsingResult
from Crawler.ChefkochModels import CategoryModel, RecipeModel

class TestContentParser(unittest.TestCase):
    def setUp(self):
        self.parser = ContentParser()
        # Load test HTML file
        test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'Data', 'testFile.html')
        with open(test_file_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def test_parse_with_html_content(self):
        # Test parsing the actual HTML content
        result = self.parser.parse(self.html_content, isRecipe=False)
        
        # Check that parser found the category URL
        category_urls = []
        # Collect all category URLs from the ParsingResult
        for pattern in self.parser.patterns:
            if hasattr(pattern, 'get_collected_entities'):
                for entity in pattern.get_collected_entities():
                    if isinstance(entity, CategoryModel) and entity.url:
                        category_urls.append(entity.url)
        
        # Verify the category URL was found
        self.assertIn("https://www.chefkoch.de/rs/s0o6/Rezepte.html", category_urls)
    
    def test_parse_recipe_in_html(self):
        # Test parsing for recipe URLs
        result = self.parser.parse(self.html_content, isRecipe=True)
        
        # Check all patterns for recipe URLs
        recipe_urls = []
        for pattern in self.parser.patterns + self.parser.recipePatterns:
            if hasattr(pattern, 'get_collected_entities'):
                for entity in pattern.get_collected_entities():
                    if isinstance(entity, RecipeModel) and entity.url:
                        recipe_urls.append(entity.url)
        
        # Verify the recipe URL was found
        target_url = "https://www.chefkoch.de/rezepte/644981165672475/Das-beste-Kartoffelgratin.html"
        # Strip query parameters for comparison
        found = any(target_url in url for url in recipe_urls)
        self.assertTrue(found, f"Recipe URL {target_url} not found in {recipe_urls}")
    
    def test_parse_empty_content(self):
        # Test with empty content
        result = self.parser.parse("", isRecipe=False)
        
        # Verify the result
        self.assertIsInstance(result, ParsingResult)
        self.assertIsInstance(result.entity, CategoryModel)
        self.assertEqual(result.entity.name, "")
        self.assertEqual(result.entity.url, "")

if __name__ == '__main__':
    unittest.main()