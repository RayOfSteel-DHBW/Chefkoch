from collections import deque
import requests
from ContentParser import ContentParser
from ChefkochDataService import ChefkochDataService
from ChefkochModels import RecipeModel, CategoryModel, IngredientModel
from ParsingResult import ParsingResult

class ChefkochCrawler:
    def __init__(self, api, dataService):
        self.data_service = dataService
        self.api = api
        self.content_parser = ContentParser()
        self.url_queue = deque()
        self.visited_urls = set()
        self.fallback_url = "https://www.chefkoch.de/rezepte/"
        
    def run(self)->bool:
        initial_categories = self.data_service.getCategories()
        if initial_categories:
            for category in initial_categories:
                self.url_queue.enqueue_entity(category.url)
        else:

            self.url_queue(self.fallback_url)
        
        while len(self.url_queue) > 0:
            try:
                url = self.url_queue.popleft()
                if url in self.visited_urls:
                    continue
                self.process_page(url)
                
            except Exception as e:
                print(f"Error processing {url}:\n{e}")
                continue
        
    def process_page(self, url):
        """Process a page for info/links it contains"""
        content = self._fetch_url(url)
        if content:
            is_recipe = url.startswith(self.fallback_url)
            if is_recipe:
                entity = RecipeModel(url=url)
            else:
                entity = CategoryModel(url=url)
            parsingResult = self.content_parser.parse(content, entity, is_recipe)
            self.enqueue_results(parsingResult)
            if parsingResult:
                self.data_service.Create_Entity(parsingResult, is_recipe)

            else:
                print(f"Unable to process {url}")
            
    def enqueue_results(self, result:ParsingResult):
        """Add found entities to the queue if they are not already visited"""
        for entity in result.
            if entity.url and entity.url not in self.visited_urls:
                self.url_queue.append(entity.url)
            
            
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