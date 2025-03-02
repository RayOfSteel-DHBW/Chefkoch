import re
from bs4 import BeautifulSoup
from streamlit import query_params
from ChefkochDataService import ChefkochEntityModel, IngredientModel, CategoryModel, RecipeModel
from ParsingResult import ParsingResult

class ContentParser():
    def __init__(self):
        self.rs_pattern = re.compile(r'\/rs\/(?:[A-z]\d{1,4}){1,7}\/(?:[A-z]+-?[A-z])+.html')
        self.rezepte_pattern = re.compile(r'/rezepte/\d{5}\/[A-z]+-?[A-z]+.html')
        self.parameter_pattern = re.compile(r'([A-Za-z])(\d{1,4})')
    
    def get_params_from_url(self, url:str)->dict:
        result = dict()
        urlParts = url.split('/')
        if len(urlParts) == 6:
            result["file"] = urlParts[-1]
            result["dir"] = urlParts[-2]
            if urlParts[3] == "rs":
                query_string = result["dir"]
                params = re.split(self.parameter_pattern, query_string)
                for i in range(1, len(params)):
                    value = params[i]
                    if(value != "" and not value.isnumeric()):
                        result[value] = params[i+1]
        else:
            return None
        return result
    
    def parse(self, content, entity:ChefkochEntityModel, is_recipe, url):
        if entity is not None:
            result = ParsingResult(entity)
            query_params = self.get_params_from_url(url)
            entity.name = self.find_first_h1(content)
            entity.file = query_params["file"]
            if is_recipe:
                entity.categories = self.parse_recipe_categories(content)
                entity.ingredients = self.parse_ingredients_table(content)
                entity.rating = self.parse_average_rating(content)
                entity.recipe_id = query_params["dir"]
            else:
                entity.current_page = query_params["s"]
                entity.category_id = query_params["t"]     
        else:
            # entity is None = we are on the main page
            result = ParsingResult(None)
            
        for match in self.rs_pattern.findall(content):
            if("t" in match.split('/')[2]):
                result.foundCategories.append(f"https://www.chefkoch.de{match}")

        result.foundRecipes = [f"https://www.chefkoch.de{match[0]}" for match in self.rezepte_pattern.findall(content)]
        
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
                    ingredients.append({'name': ingredient, 'amount': quantity})
        
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