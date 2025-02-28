import re
from bs4 import BeautifulSoup
from ChefkochDataService import IngredientModel, CategoryModel, RecipeModel
from ParsingResult import ParsingResult

class ContentParser():
    def __init__(self):
        self.rs_pattern = re.compile(r'\/rs\/([A-z]\d{1,4}){1,7}\/([A-z]+-?[A-z])+.html')
        self.rezepte_pattern = re.compile(r'/rezepte/\d{5}\/[A-z]+-?[A-z]+.html')
        self.parameter_pattern = re.compile(r"'(\d+)")
    
    def get_params_from_url(self, entity)->dict:
        split = re.split(self.parameter_pattern, entity.url.split('/')[-2])
        return {split[i]: split[i+1] for i in range(0, len(split), 2)}
        
    def parse(self, content, entity, is_recipe):
        if entity is not None:
            entity.name = self.find_first_h1(content)
            entity.url = entity.url
            if is_recipe:
                entity.categories = self.rs_pattern.findall(content)
                entity.ingredients = self.parse_ingredients_table(content)
                entity.rating = self.parse_average_rating(content)
            else:
                entity.name = self.find_first_h1(content)
                entity.url = entity.url
                result = ParsingResult(entity)
        else:
            # entity is None = we are on the main page
            result = ParsingResult(None)
            result.foundCategories = self.parse_main_page(content)
            res
                    
                               
        
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