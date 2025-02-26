from ChefkochContracts import Ingredient, Category, Recipe
from ContentParser import ContentParser

class ChefkochAPI:
    def GetLinkedObjects(self, entity):
        """
        Returns a list of linked objects for a given entity.
        For recipes additional parsers are added in the ContentParser.
        """
        page_content = self._get_page_content(entity)
        if(not page_content):
            return None
        
        if isinstance(entity, Category):
            return ContentParser.Parse(page_content, False)
        elif isinstance(entity, Recipe):
            return ContentParser.Parse(page_content, True)
        else:
            return []

    def _get_page_content(self, entity)->str:
        """Fetches the page content for a given entity."""
        # Implement the logic to fetch the page content based on the entity
        return ""

    def _get_recipes_for_category(self, category: Category) -> list[Recipe]:
        """Returns all recipes for a given category."""
        return []

    def _get_ingredients_for_recipe(self, recipe: Recipe) -> list[Ingredient]:
        """Returns all ingredients for a given recipe."""
        return []