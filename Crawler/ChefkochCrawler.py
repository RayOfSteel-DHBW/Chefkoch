import requests
from collections import deque
from ChefkochContracts import ChefkochEntity, Category, Recipe, Ingredient

class ChefkochCrawler:
    def __init__(self, api, dataService) -> None:
        self.api = api
        self.dataService = dataService
        self.ProcessingQueue = deque()

    def process_entity(self, entity: ChefkochEntity) -> None:
        """
        Processes a top entity by fetching its linked objects.
        - Creates Ingredient objects immediately.
        - For any ChefkochEntity, checks the URL and creates it if the response is 200.
        - If created successfully:
          - Recipes are queued to the left (for immediate processing).
          - Categories are queued to the right.
        """
        # Retrieve linked objects using the API's GetLinkedObjects method.
        linked_objects = self.api.GetLinkedObjects(entity)
        for obj in linked_objects:
            if isinstance(obj, Ingredient):
                # Immediately create ingredients.
                self.dataService.create_or_update_entity(obj)
            elif isinstance(obj, ChefkochEntity):
                try:
                    response = requests.get(obj.url)
                    if response.status_code == 200:
                        created = self.dataService.create_or_update_entity(obj)
                        if created:
                            # Queue Recipes to the left and Categories to the right.
                            if isinstance(obj, Recipe):
                                self.ProcessingQueue.appendleft(obj)
                            elif isinstance(obj, Category):
                                self.ProcessingQueue.append(obj)
                    else:
                        print(f"URL check failed for {obj.name}: status {response.status_code}")
                except Exception as e:
                    print(f"Error accessing URL for {obj.name}: {e}")

    def run(self) -> bool:
        """
        Initializes the processing queue with known categories and processes them.
        Recipes are processed before categories as they are added to the left.
        """
        try:
            # Initialize the queue with top-level entities (e.g., known categories).
            top_entities = self.dataService.getCategories()
            for entity in top_entities:
                self.ProcessingQueue.append(entity)

            while self.ProcessingQueue:
                current_entity = self.ProcessingQueue.popleft()
                self.process_entity(current_entity)

            return True
        except Exception as e:
            print(f"Error during crawling: {e}")
            return False
