
from ChefkochAPI import ChefkochAPI
from ChefkochCrawler import ChefkochCrawler

from ChefkochDataService import ChefkochDataService

def main() -> None:
    crawler = InitializeCrawler()
    try:
        successfulCompletion = crawler.run()
        if successfulCompletion:
            print("Crawler completed successfully.")
        else:
            print("Crawler did not complete successfully.")
    except Exception as e:
        print(f"Error during initialization: {e}")


def InitializeCrawler():
    dbPath = r"..\Data\chefkoch.db"
    dataService = ChefkochDataService(dbPath)
    api = ChefkochAPI() 
    crawler = ChefkochCrawler(api, dataService)
    return crawler

if __name__ == "__main__":
    main()