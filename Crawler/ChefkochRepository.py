from abc import ABC, abstractmethod
from typing import List
from ChefkochContracts import Category, Recipe, Ingredient, Tag

class ChefkochRepository(ABC):
    """
    Abstract repository interface for Chefkoch data.
    Implementations may use SQLite, PostgreSQL, etc.
    """
    
    # Standard-Kategorien mit Links
    DEFAULT_CATEGORIES: List[Category] = [
        Category("Auflauf", "https://www.chefkoch.de/rs/s0t30/Auflauf-Rezepte.html"),
        Category("Pizza", "https://www.chefkoch.de/rs/s0t82/Pizza-Rezepte.html"),
        Category("Reis- oder Nudelsalat", "https://www.chefkoch.de/rs/s0t94/Reis-oder-Nudelsalat-Rezepte.html"),
        Category("Salat", "https://www.chefkoch.de/rs/s0t15/Salat-Rezepte.html"),
        Category("Salatdressing", "https://www.chefkoch.de/rs/s0t3669/Salatdressing-Rezepte.html"),
        Category("Tarte", "https://www.chefkoch.de/rs/s0t122/Tarte-Rezepte.html"),
        Category("Fingerfood", "https://www.chefkoch.de/rs/s0t52/Fingerfood-Rezepte.html"),
        Category("Dips", "https://www.chefkoch.de/rs/s0t35/Dips-Rezepte.html"),
        Category("Saucen", "https://www.chefkoch.de/rs/s0t34/Saucen-Rezepte.html"),
        Category("Suppe", "https://www.chefkoch.de/rs/s0t40/Suppe-Rezepte.html"),
        Category("Klöße", "https://www.chefkoch.de/rs/s0t166/Kloesse-Rezepte.html"),
        Category("Brot und Brötchen", "https://www.chefkoch.de/rs/s0t108/Brot-und-Broetchen-Rezepte.html"),
        Category("Brotspeise", "https://www.chefkoch.de/rs/s0t46/Brotspeise-Rezepte.html"),
        Category("Aufstrich", "https://www.chefkoch.de/rs/s0t51/Aufstrich-Rezepte.html"),
        Category("Süßspeise", "https://www.chefkoch.de/rs/s0t89/Suessspeise-Rezepte.html"),
        Category("Eis", "https://www.chefkoch.de/rs/s0t127/Eis-Rezepte.html"),
        Category("Kuchen", "https://www.chefkoch.de/rs/s0t92/Kuchen-Rezepte.html"),
        Category("Kekse", "https://www.chefkoch.de/rs/s0t147/Kekse-Rezepte.html"),
        Category("Torte", "https://www.chefkoch.de/rs/s0t93/Torte-Rezepte.html"),
        Category("Confiserie", "https://www.chefkoch.de/rs/s0t157/Confiserie-Rezepte.html"),
        Category("Getränke", "https://www.chefkoch.de/rs/s0t11/Getraenke-Rezepte.html"),
        Category("Shake", "https://www.chefkoch.de/rs/s0t113/Shake-Rezepte.html"),
        Category("Gewürzmischung", "https://www.chefkoch.de/rs/s0t313/Gewuermischung-Rezepte.html"),
        Category("Pasten", "https://www.chefkoch.de/rs/s0t243/Pasten-Rezepte.html"),
        Category("Studentenküche", "https://www.chefkoch.de/rs/s0t211/Studentenkueche-Rezepte.html"),
    ]
    
    @abstractmethod
    def category_exists(self, category_name: str) -> bool:
        pass

    @abstractmethod
    def save_category(self, category: Category) -> None:
        pass

    @abstractmethod
    def get_category_page(self, category_name: str) -> int:
        pass

    @abstractmethod
    def update_category_page(self, category_name: str, page: int) -> None:
        pass

    @abstractmethod
    def recipe_exists(self, recipe_id: str) -> bool:
        pass

    @abstractmethod
    def save_recipe(self, recipe: Recipe) -> None:
        pass

    @abstractmethod
    def save_ingredients(self, recipe_id: str, ingredients: List[Ingredient]) -> None:
        pass

    @abstractmethod
    def save_tags(self, recipe_id: str, tags: List[Tag]) -> None:
        pass

    # Optional: Methode zum Initialisieren der Kategorien in der DB
    @abstractmethod
    def initialize_categories(self, categories: List[Category]) -> None:
        pass