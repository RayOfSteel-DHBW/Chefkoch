from collections import deque
import requests
from ContentParser import ContentParser
from ChefkochDataService import ChefkochDataService
from ChefkochModels import RecipeModel, CategoryModel, IngredientModel

class ChefkochCrawler:
    def __init__(self, api, dataService):
        self.data_service = dataService
        self.api = api
        self.content_parser = ContentParser()
        self.entity_queue = deque()
        self.visited_urls = set()
        
    def run(self)->bool:
        initial_categories = self.data_service.getCategories()
        for category in initial_categories:
            self.enqueue_entity(category)
        
        while len(self.entity_queue) > 0:
            try:
                entity = self.entity_queue.popleft()
                url = entity.url
                if url in self.visited_urls:
                    continue
                
                content = self._fetch_url(url)
                
                if content:
                    self.process_page(content, url, entity)
            except Exception as e:
                print(f"Error processing entity {getattr(entity, 'url', 'unknown')}: {str(e)}")
                # Continue with the next entity in the queue
                continue
    
    def process_page(self, html_content, url, entity):
        """Process a page (recipe or category) and store/extract data"""
        is_recipe = isinstance(entity, RecipeModel)
        
        result = self.content_parser.parse(html_content, isRecipe=is_recipe, url=url)
        
        # For recipes, store the data
        if is_recipe:
            recipe_model = result.entity
            if recipe_model and recipe_model.name:
                self.data_service.create_recipe_with_relations(
                    recipe_model,
                    recipe_model.ingredients,
                    recipe_model.categories
                )
            else:
                print(f"Could not extract recipe from {url}")
        
        # Add newly found entities to the queue
        self._enqueue_found_entities(result)
        
        return result.entity if is_recipe else None
            
    def _enqueue_found_entities(self, result):
        """Process found URLs from parsing result and add to queue"""
        # Add recipes (higher priority - left)
        for url in result.foundRecipes:
            if url not in self.visited_urls:
                recipe = RecipeModel(name=None, url=url)  # Name will be populated when we process it
                self.enqueue_entity(recipe)
                
        # Add categories (lower priority - right)
        for url in result.foundCategories:
            if url not in self.visited_urls:
                # Extract category ID from URL if possible
                try:
                    category_id = int(url.split('/')[-2].replace('s', ''))
                except (IndexError, ValueError):
                    category_id = 0
                    
                category = CategoryModel(
                    name="", 
                    url=url, 
                    external_id=category_id
                )  # Name will be populated when we process it
                self.enqueue_entity(category)
            
    def enqueue_entity(self, entity):
        """Add entity to queue with priority based on type"""
        if entity.url in self.visited_urls:
            return
        
        if isinstance(entity, RecipeModel):
            # Higher priority - add to the left (front)
            self.entity_queue.appendleft(entity)
        else:
            # Lower priority - add to the right (back)
            self.entity_queue.append(entity)
            
    def _fetch_url(self, url):
        """Fetch content from URL with error handling"""
        # Add domain if the URL is relative
        if url.startswith('/'):
            url = f"https://www.chefkoch.de{url}"
            
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0'})
        try:
            response.raise_for_status()
            self.visited_urls.add(url)  # Mark URL as visited after successful fetch
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        return response.text
    
    # Removed _create_ingredient_models and _create_category_models methods
    # since we're working directly with models now