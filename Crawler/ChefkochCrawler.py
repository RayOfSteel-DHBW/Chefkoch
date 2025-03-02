from collections import deque
import requests
from ContentParser import ContentParser
from ChefkochDataService import CategoryModel, RecipeModel
from ParsingResult import ParsingResult

class ChefkochCrawler:
    def __init__(self, data_service):
        self.data_service = data_service
        self.content_parser = ContentParser()
        self.url_queue = deque()
        self.visited_urls = set()
        self.fallback_url = "https://www.chefkoch.de/rezepte"
        
    def run(self)->bool:
        initial_categories = self.data_service.get_categories_for_update()
        
        if initial_categories.count() > 0:
            for category in initial_categories:
                self.url_queue.enqueue_entity(category.url)
        else:
            self.url_queue.append(self.fallback_url)
        
        while len(self.url_queue) > 0:
            url = self.url_queue.popleft()
            if url in self.visited_urls:
                continue
            else:
                self.process_page(url)
            
        return True
        
    def process_page(self, url):
        """Process a page for info/links it contains"""
        content = self._fetch_url(url)
        if content:
            is_recipe = url.startswith("https://www.chefkoch.de/rezepte/")
            if is_recipe:
                entity = RecipeModel()
            elif url.startswith("https://www.chefkoch.de/rs/"):
                entity = CategoryModel()
            else:
                entity = None
            parsingResult = self.content_parser.parse(content, entity, is_recipe, url)
            if parsingResult:
                self.enqueue_results(parsingResult)
                if parsingResult.entity:
                    self.data_service.process_entity(parsingResult.entity)
            else:
                print(f"Unable to process {url}")
            
    def enqueue_results(self, result:ParsingResult):
        """Add found entities to the queue if they are not already visited"""
        for entity in result.foundCategories:
            if entity not in self.visited_urls:
                self.url_queue.append(entity)
        for entity in result.foundRecipes:
            if entity not in self.visited_urls:
                self.url_queue.appendleft(entity)
            
            
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