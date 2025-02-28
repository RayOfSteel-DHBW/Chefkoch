import re
from bs4 import BeautifulSoup
from ChefkochDataService import IngredientModel, CategoryModel, RecipeModel
from ParsingResult import ParsingResult

class ContentParser():
    def __init__(self):
        self.rs_pattern = re.compile(r'/rs/([a-zA-Z0-9]+)/([a-zA-Z0-9-]+)\.html')
        self.rezepte_pattern = re.compile(r'/rs/s0(.+)/[a-zA-z0-9-]+.html')
            
    def parse(self, content, entity, is_recipe):
        if is_recipe:
            entity.name = self.find_first_h1(content)
            entity.url = entity.url
            entity.categories = self.rs_pattern.findall(content)
            entity.ingredients = self.parse_ingredients_table(content)
            entity.rating = self.parse_average_rating(content)
        result = ParsingResult(entity)
        
        rs_matches = self.rs_pattern.findall(content)
        rezepte_matches = self.rezepte_pattern.findall(content)
        
        result.foundCategories = [CategoryModel(url=f"https://www.chefkoch.de{match[0]}") for match in rs_matches]
        result.foundRecipes = [RecipeModel(url=f"https://www.chefkoch.de{match[0]}") for match in rezepte_matches]
        
        return result

    def parse_ingredients_table(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', {'class': 'ingredients table-header'})
        ingredients = []
        
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    quantity = cols[0].get_text(strip=True)
                    ingredient = cols[1].get_text(strip=True)
                    ingredients.append(IngredientModel(name=ingredient, amount=quantity))
        
        return ingredients

    def find_first_h1(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        h1 = soup.find('h1')
        return h1.get_text(strip=True) if h1 else None

    def parse_average_rating(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        rating_div = soup.find('div', {'class': 'ds-rating-avg'})
        if rating_div:
            rating_strong = rating_div.find('strong')
            if rating_strong:
                return rating_strong.get_text(strip=True)
        return None