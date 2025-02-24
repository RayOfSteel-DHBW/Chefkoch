from ChefkochAPI import ChefkochAPI
from ChefkochSQLiteDataService import ChefkochSQLiteDataService
from ChefkochCrawler import ChefkochCrawler
from ChefkochRepository import ChefkochRepository

def main() -> None:
    # Erzeuge Repository und API
    repo = ChefkochSQLiteDataService(r"..\Data\chefkoch.db")
    api = ChefkochAPI()
    
    # Falls noch keine Kategorien in der DB vorhanden sind, initialisiere sie
    cursor = repo.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    if count == 0:
        for cat in ChefkochRepository.DEFAULT_CATEGORIES:
            repo.save_category(cat)
    
    # Starte den Crawler, der nun die in der DB hinterlegten Kategorien verwendet
    crawler = ChefkochCrawler(api, repo)
    crawler.run()

if __name__ == "__main__":
    main()