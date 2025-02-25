from Crawler import ChefkochAPI, ChefkochDataService
from ChefkochContracts import Category, ChefkochEntity, Recipe
from collections import deque
class ChefkochCrawler:
    def __init__(self, api: ChefkochAPI, dataService: ChefkochDataService) -> None:
        self.api = api
        self.dataService = dataService

    def HandleUnconfirmedEntity(self, entity: ChefkochEntity) -> None:
        resultEntities = self.api.GetLinkedEntities(entity)
        for result in resultEntities:
            created = self.dataService.create_or_update_entity(result)
            if created:
                if(isinstance(result, Category)):
                    self.ProcessingQueue.append(result)
                elif(isinstance(result, Recipe)):
                    self.ProcessingQueue.appendleft(result)

                        
    def run(self) -> bool:
        try:
            knownCategories = self.dataService.getCategories()
            self.ProcessingQueue = deque()
            for category in knownCategories:
                self.ProcessingQueue.put(category)
            while not self.ProcessingQueue.empty():
                try:
                    entity = self.ProcessingQueue.popleft()
                    self.HandleUnconfirmedEntity(entity)
                except Exception as e:
                    print(f"Error handling entity: {e}")
                    continue
            return True
                
                
 
                
            return True
        except Exception as e:
            print(f"Error during crawling: {e}")
            return False
        
        
        