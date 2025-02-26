from PatternBase import PatternBase
from ParsingPatterns import (
    CategoryPattern, RezeptePattern, CategoryTagPattern, 
    IngredientTablePattern, RecipeTitlePattern
)
from ChefkochContracts import Recipe
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
        entity = Recipe("", url) if isRecipe else None
        result = ParsingResult(entity=entity, foundRecipes=[], foundCategories=[])
        
        # Set the result on all patterns
        for pattern in self.patterns:
            pattern.set_result(result)
            
        if isRecipe:
            for pattern in self.recipePatterns:
                pattern.set_result(result)
        
        # Process all patterns
        usedPatterns = self.patterns.copy()
        if isRecipe:
            usedPatterns.extend(self.recipePatterns)
            
        # Process character by character
        for character in content:                
            for pattern in usedPatterns:
                pattern.check_character(character)
        
        return result
