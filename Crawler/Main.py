
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
 
    dataService = ChefkochDataService()
    crawler = ChefkochCrawler(dataService)
    return crawler

if __name__ == "__main__":
    main()