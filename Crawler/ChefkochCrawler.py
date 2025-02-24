import re
from ChefkochAPI import ChefkochAPI
from ChefkochRepository import ChefkochRepository

class ChefkochCrawler:
    def __init__(self, api: ChefkochAPI, repo: ChefkochRepository) -> None:
        self.api = api
        self.repo = repo
        self.categories = [
            "Auflauf",
            "Pizza",
            "Reis- oder Nudelsalat",
            "Salat",
            "Salatdressing",
            "Tarte",
            "Fingerfood",
            "Dips",
            "Saucen",
            "Suppe",
            "Klöße",
            "Brot und Brötchen",
            "Brotspeise",
            "Aufstrich",
            "Süßspeise",
            "Eis",
            "Kuchen",
            "Kekse",
            "Torte",
            "Confiserie",
            "Getränke",
            "Shake",
            "Gewürzmischung",
            "Pasten",
            "Studentenküche"
        ]
        self._initialize_categories()

    def _initialize_categories(self) -> None:
        for category in self.categories:
            if not self.repo.category_exists(category):
                self.repo.save_category(category)

    def run(self, chunk_size: int = 1) -> None:
        for category_name in self.categories:
            page = self.repo.get_category_page(category_name)
            while True:
                recipes = self.api.getRecipes_for_page(category_name, page)
                if not recipes:
                    # Reset page if no more recipes on this page.
                    self.repo.update_category_page(category_name, 0)
                    break
                for recipe in recipes:
                    recipe_id = self._extract_recipe_id(recipe.url)
                    if not self.repo.recipe_exists(recipe_id):
                        self.repo.save_recipe(recipe)
                        self.repo.save_ingredients(recipe_id, recipe.ingredients)
                        self.repo.save_tags(recipe_id, recipe.tags)
                page += 1
                self.repo.update_category_page(category_name, page)

    def _extract_recipe_id(self, recipe_url: str) -> str:
        match = re.search(r"/rezepte/(\d+)", recipe_url)
        return match.group(1) if match else recipe_url