from collections import deque
import requests
from ContentParser import ContentParser
from ChefkochDataService import ChefkochDataService
from ChefkochContracts import Recipe, Category, ChefkochEntity
from ChefkochModels import RecipeModel, CategoryModel, IngredientModel

class ChefkochCrawler:
    def __init__(self, api, dataService):
        self.data_service = dataService
        self.api = api
        self.content_parser = ContentParser()
        self.entity_queue = deque()
        self.visited_urls = set()
        
    def run(self):

        initial_categories = self.data_service.getCategories()
        for category in initial_categories:
            domainCategory = category.ToDomainObject()
            self.enqueue_entity(domainCategory))
        
        while len(self.entity_queue) > 0:
            entity = self.entity_queue.popleft()
            url = entity.url
            if url in self.visited_urls:
                continue
                
            content = self._fetch_url(url)
            if(content):
                if isinstance(entity, Recipe):
                    self.process_recipe_page(content, url)
                else:
                    self.process_category_page(content, url)
    
    def process_recipe_page(self, html_content, recipe_url):
        """Process a recipe page and store its data"""
        # Parse the content
        result = self.content_parser.parse(html_content, isRecipe=True, url=recipe_url)
        
        # Extract the recipe entity from the result
        recipe_entity = result.entity
        
        if not recipe_entity or not recipe_entity.name:
            print(f"Could not extract recipe from {recipe_url}")
            return None
            
        # Convert entities to models using to_model()
        recipe_model = recipe_entity.to_model()
        ingredient_models = [i.to_model() for i in recipe_entity.ingredients]
        category_models = [c.to_model() for c in recipe_entity.categories]
        
        # Store in database
        recipe = self.data_service.create_recipe_with_relations(
            recipe_model, ingredient_models, category_models
        )
        
        # Add newly found entities to the queue
        self._enqueue_found_entities(result)
            
        return recipe
        
    def process_category_page(self, html_content, category_url):
        """Process a category page and extract recipes and subcategories"""
        # Parse the content
        result = self.content_parser.parse(html_content, isRecipe=False, url=category_url)
        
        # Add all found entities to the queue
        self._enqueue_found_entities(result)
            
    def _enqueue_found_entities(self, result):
        """Process found URLs from parsing result and add to queue"""
        # Add recipes (higher priority - left)
        for url in result.foundRecipes:
            if url not in self.visited_urls:
                recipe = Recipe("", url)  # Name will be populated when we process it
                self.enqueue_entity(recipe)
                
        # Add categories (lower priority - right)
        for url in result.foundCategories:
            if url not in self.visited_urls:
                # Extract category ID from URL if possible
                try:
                    category_id = int(url.split('/')[-2].replace('s', ''))
                except (IndexError, ValueError):
                    category_id = 0
                    
                category = Category("", url, category_id)  # Name will be populated when we process it
                self.enqueue_entity(category)
            
    def enqueue_entity(self, entity):
        """Add entity to queue with priority based on type"""

        if entity.url in self.visited_urls:
            return
        
        if isinstance(entity, Recipe):
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
    
    def _create_ingredient_models(self, ingredients):
        """Convert ingredient entities to models and store them"""
        models = []
        for ingredient in ingredients:
            model = IngredientModel.get_or_create(
                name=ingredient.name,
                defaults={'amount': ingredient.amount}
            )[0]
            models.append(model)
        return models
    
    def _create_category_models(self, categories):
        """Convert category entities to models and store them"""
        models = []
        for category in categories:
            model = CategoryModel.get_or_create(
                name=category.name,
                defaults={
                    'url': category.url,
                    'external_id': category.ID
                }
            )[0]
            models.append(model)
        return models