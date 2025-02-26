from ChefkochModels import CategoryModel, RecipeModel
from PatternBase import PatternBase
from ParsingPatterns import (
    CategoryPattern, RezeptePattern, CategoryTagPattern, 
    IngredientTablePattern, RecipeTitlePattern
)
from ChefkochContracts import Category, Recipe
from ParsingResult import ParsingResult

class ContentParser():
    def __init__(self):
        # Basic patterns that just return strings
        self.patterns = [CategoryPattern(), RezeptePattern()]
        
        # Entity-producing patterns
        self.recipePatterns = [
            CategoryTagPattern(),
            IngredientTablePattern(),
            RecipeTitlePattern()
        ]
            
    def parse(self, content, isRecipe=False, url="") -> ParsingResult:
        # Create result with an empty entity
        entity = RecipeModel("", url) if isRecipe else CategoryModel("", url)
        result = ParsingResult(entity)
        # Process all patterns
        usedPatterns = self.patterns.copy()
        if isRecipe:
            usedPatterns.extend(self.recipePatterns)
            
        # Process character by character
        for character in content:                
            for pattern in usedPatterns:
                result = pattern.check_character(character)
        
        return result
