from ParsingPatterns import (
    CategoryPattern, RezeptePattern, CategoryTagPattern, 
    IngredientTablePattern, RecipeTitlePattern
)
from ParsingResult import ParsingResult

class ContentParser():
    def __init__(self):
        # Basic patterns that just return strings
        self.patterns = [
            CategoryPattern(), 
            RezeptePattern()]
        
        # Gets linked categories and ingredients as well as the recipe title
        self.recipePatterns = [
            CategoryTagPattern(),
            IngredientTablePattern(),
            RecipeTitlePattern()
        ]
            
    def parse(self, content, entity, is_recipe) -> ParsingResult:

        result = ParsingResult()
        result.entity = entity
        # Add recipe patterns if needed
        usedPatterns = self.patterns.copy()
        if is_recipe:
            usedPatterns.extend(self.recipePatterns)

        # Process character by character
        for character in content:                
            for pattern in usedPatterns:
                result = pattern.check_character(character, result)
        
        return result
