
from ChefkochCrawler import ChefkochCrawler

from ChefkochDataService import ChefkochDataService

def main() -> None:
    crawler = InitializeCrawler()
    successfulCompletion = crawler.run()
    if successfulCompletion:
        print("Crawler completed successfully.")
    else:
        print("Crawler did not complete successfully.")



def InitializeCrawler():
 
    dataService = ChefkochDataService()
    crawler = ChefkochCrawler(dataService)
    return crawler

if __name__ == "__main__":
    main()