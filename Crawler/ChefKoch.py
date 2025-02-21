import requests
from bs4 import BeautifulSoup
from ChefkochContracts import Category, Ingredient, Recipe, Tag
import json
import csv
import os
from typing import List, Optional




class ChefkochAPI:
    """
    Handles all network calls to Chefkoch.de,
    including retrieving categories, recipes, etc.
    """

    def __init__(self) -> None:
        self.base_url: str = "https://www.chefkoch.de"

    def beautify_text(self, text: str) -> str:
        """
        Removes newlines/tabs, multiple spaces, and trims the text.
        """
        text = text.replace("\r", "").replace("\n", "").replace("\t", "")
        while "  " in text:
            text = text.replace("  ", " ")
        return text.strip()

    def getCategories(self) -> List[Category]:
        """
        Returns a fixed list of Category objects. Each Category.url is the
        full link (including https://...) to the 'page 0' (s0) of that category.
        """
        return [
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

    def getCategory(self, category_sub_url: str) -> Optional[Category]:
        """
        Given a *relative* category URL (e.g. '/rs/s0/Pizza/Rezepte.html'),
        fetch the page and derive a Category object from its <h1> title.
        """
        full_url = self.base_url + category_sub_url
        resp = requests.get(full_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        h1 = soup.find("h1")
        if not h1:
            return None

        text = self.beautify_text(h1.get_text())
        # e.g. "Pizza Rezepte" → "Pizza"
        if " Rezepte" in text:
            text = text.split(" Rezepte")[0].strip()

        return Category(name=text, url=category_sub_url)

    def get_recipe(self, recipe_sub_url: str) -> Recipe:
        """
        Fetch full info for a single recipe, given its sub-URL or a full URL.
        If recipe_sub_url starts with "http", we assume it’s already absolute.
        Otherwise, we prepend self.base_url.
        """
        if recipe_sub_url.startswith("http"):
            full_url = recipe_sub_url
        else:
            full_url = self.base_url + recipe_sub_url

        resp = requests.get(full_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        h1 = soup.find("h1")
        recipe_name = self.beautify_text(h1.get_text()) if h1 else "No recipe name"

        # Extract ingredients:
        ingredient_list: List[Ingredient] = []
        table = soup.find("table", class_="ingredients")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                right_td = row.find("td", class_="td-right")
                left_td = row.find("td", class_="td-left")
                if right_td:
                    ing_name = self.beautify_text(right_td.get_text())
                else:
                    ing_name = "No ingredient name found"

                if left_td:
                    ing_amount = self.beautify_text(left_td.get_text())
                else:
                    ing_amount = "No ingredient amount found"

                ingredient_list.append(Ingredient(name=ing_name, amount=ing_amount))

        # Extract category from breadcrumbs:
        category_obj: Optional[Category] = None
        breadcrumb = soup.find("ol", class_="ds-col-12")
        if breadcrumb:
            li_items = breadcrumb.find_all("li")
            # 4th item in breadcrumb is typically the category
            if len(li_items) > 3:
                cat_link = li_items[3].find("a")
                if cat_link and cat_link.get("href"):
                    category_sub_url = cat_link["href"]
                    category_obj = self.getCategory(category_sub_url)

        # Extract tags:
        tags_list: List[Tag] = []
        tag_div = soup.find("div", class_="recipe-tags")
        if tag_div:
            for t in tag_div.find_all("a"):
                tag_name = self.beautify_text(t.get_text())
                tag_href = t.get("href") or "none"
                tags_list.append(Tag(name=tag_name, url=tag_href))
        else:
            tags_list.append(Tag("No tags found", "none"))

        return Recipe(
            name=recipe_name,
            url=recipe_sub_url,
            ingredients=ingredient_list,
            category=category_obj,
            tags=tags_list
        )

    def getRecipes(
        self,
        category: Category,
        end_index: int = 5,
        start_index: int = 0
    ) -> List[Recipe]:
        """
        Fetch all recipes for a given Category, iterating from `start_index` to `end_index`.
        Each page is derived by replacing '/s0t' with '/s{i}t' in the category URL.
        """
        original_url = category.url
        all_recipes: List[Recipe] = []

        for i in range(start_index, end_index + 1):
            # Convert "/rs/s0t123/..." → "/rs/s{i}t123/..."
            page_url = original_url.replace("/s0t", f"/s{i}t")

            resp = requests.get(page_url)
            if resp.status_code != 200:
                # Could break or continue; you decide how to handle a non‐200
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            recipe_cards = soup.find_all("div", class_="ds-recipe-card")

            for card in recipe_cards:
                h3 = card.find("h3")
                if not h3:
                    continue
                card_name = self.beautify_text(h3.get_text())

                link_tag = card.find("a")
                if not link_tag:
                    continue
                recipe_sub_url = link_tag.get("href").split("#")[0]

                # Fetch the single recipe details using get_recipe():
                recipe_obj = self.get_recipe(recipe_sub_url)

                # Override category with the known one
                recipe_obj.category = category
                # Update name with the card_name from the listing
                recipe_obj.name = card_name

                all_recipes.append(recipe_obj)

        return all_recipes

    def getAllRecipes(self, end_index: int = 5, start_index: int = 0) -> List[Recipe]:
        """
        Fetch all recipes from all categories in the static list.
        Potentially expensive if end_index is large.
        """
        categories = self.getCategories()
        everything: List[Recipe] = []

        for cat in categories:
            cat_recipes = self.getRecipes(cat, end_index=end_index, start_index=start_index)
            everything.extend(cat_recipes)
        return everything

    def searchRecipes(
        self,
        query: str,
        end_index: int = 5,
        start_index: int = 0
    ) -> List[Recipe]:
        """
        Execute a Chefkoch search by `query`, returning all recipes
        across pages from `start_index` to `end_index`.
        """
        results: List[Recipe] = []

        for i in range(start_index, end_index + 1):
            search_url = f"{self.base_url}/rs/s{i}/{query}/Rezepte.html"
            resp = requests.get(search_url)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            recipe_cards = soup.find_all("div", class_="ds-recipe-card")

            for card in recipe_cards:
                h3 = card.find("h3")
                if not h3:
                    continue
                card_name = self.beautify_text(h3.get_text())

                link_tag = card.find("a")
                if not link_tag:
                    continue
                recipe_sub_url = link_tag.get("href").split("#")[0]

                # Use get_recipe() consistently
                recipe_obj = self.get_recipe(recipe_sub_url)
                # Keep the listing’s name in the final object
                recipe_obj.name = card_name
                results.append(recipe_obj)

        return results


class DataParser:
    """
    Handles reading/writing recipes/categories to disk
    in JSON or CSV formats.
    """

    def write_file(self, filename: str, data: str) -> None:
        """Write raw text data to file (UTF-8)."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"[INFO] The file '{filename}' has been saved.")

    def read_file(self, filename: str) -> str:
        """Read raw text data from file (UTF-8)."""
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def write_recipes_to_json(self, recipes: List[Recipe], filename: str) -> None:
        """
        Serialize recipes to a JSON file. We convert custom objects
        to dictionaries for easy JSON dumping.
        """
        dict_list = []
        for r in recipes:
            dict_list.append({
                "name": r.name,
                "url": r.url,
                "ingredients": [
                    {"name": ing.name, "amount": ing.amount} for ing in r.ingredients
                ],
                "category": {
                    "name": r.category.name if r.category else "",
                    "url": r.category.url if r.category else ""
                },
                "tags": [
                    {"name": t.name, "url": t.url} for t in r.tags
                ]
            })
        json_data = json.dumps(dict_list, ensure_ascii=False, indent=2)
        self.write_file(filename, json_data)

    def write_categories_to_json(self, categories: List[Category], filename: str) -> None:
        """Write the list of categories to a JSON file."""
        dict_list = [{"name": c.name, "url": c.url} for c in categories]
        json_data = json.dumps(dict_list, ensure_ascii=False, indent=2)
        self.write_file(filename, json_data)

    def write_recipes_to_csv(self, recipes: List[Recipe], filename: str) -> None:
        """
        Write a minimal CSV with these columns:
        - RecipeName
        - URL
        - CategoryName
        """
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["RecipeName", "URL", "CategoryName"])
            for r in recipes:
                cat_name = r.category.name if r.category else ""
                writer.writerow([r.name, r.url, cat_name])
        print(f"[INFO] The file '{filename}' has been saved in CSV format.")

    def write_categories_to_csv(self, categories: List[Category], filename: str) -> None:
        """Write categories (name, url) to a CSV file."""
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["CategoryName", "URL"])
            for c in categories:
                writer.writerow([c.name, c.url])
        print(f"[INFO] The file '{filename}' has been saved in CSV format.")

    def load_recipes_from_json(self, filename: str) -> List[Recipe]:
        """
        Reads a JSON file of recipes, reconstructs them as Recipe objects.
        """
        data = self.read_file(filename)
        items = json.loads(data)
        recipes: List[Recipe] = []

        for item in items:
            # Build Ingredient objects
            ing_objs = [Ingredient(ing["name"], ing["amount"]) for ing in item["ingredients"]]

            # Build Category object
            cat_dict = item["category"]
            cat_obj = None
            if cat_dict and cat_dict.get("name"):
                cat_obj = Category(cat_dict["name"], cat_dict.get("url", ""))

            # Build Tag objects
            tag_objs = [Tag(t["name"], t["url"]) for t in item["tags"]]

            # Finally, create the Recipe
            recipe_obj = Recipe(
                name=item["name"],
                url=item["url"],
                ingredients=ing_objs,
                category=cat_obj,
                tags=tag_objs
            )
            recipes.append(recipe_obj)

        return recipes

    def load_categories_from_json(self, filename: str) -> List[Category]:
        """Reads a JSON file of categories, returns a list of Category objects."""
        data = self.read_file(filename)
        items = json.loads(data)
        return [Category(c["name"], c["url"]) for c in items]

    def load_recipes_from_csv(self, filename: str) -> List[Recipe]:
        """
        Loads minimal CSV with columns: name, url, categoryName.
        We cannot restore ingredients/tags from this format, so
        they’ll remain empty.
        """
        recipes: List[Recipe] = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row
            for row in reader:
                if not row or len(row) < 3:
                    continue
                name, url, cat_str = row
                cat_obj = Category(name=cat_str, url="")
                recipes.append(Recipe(name=name, url=url, ingredients=[], category=cat_obj))
        return recipes

    def load_categories_from_csv(self, filename: str) -> List[Category]:
        """
        Reads CSV with columns [CategoryName, URL].
        Returns a list of Category objects.
        """
        categories: List[Category] = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row
            for row in reader:
                if not row or len(row) < 2:
                    continue
                cat_name, cat_url = row
                categories.append(Category(cat_name, cat_url))
        return categories


if __name__ == "__main__":
    # Quick usage demo
    api = ChefkochAPI()
    parser = DataParser()

    # 1) Fetch your static categories
    print("[DEMO] Fetching categories...")
    category_list = api.getCategories()
    print(f"Found {len(category_list)} categories. Example:", category_list[:3])

    # 2) Fetch some recipes from the FIRST category
    if category_list:
        first_cat = category_list[0]
        print(f"\n[DEMO] Fetching recipes for category: '{first_cat.name}'")
        recipes = api.getRecipes(first_cat, end_index=1, start_index=0)
        print(f"Found {len(recipes)} recipes. Example entries:\n", recipes[:2])

        # 3) Save to JSON and re-load
        parser.write_recipes_to_json(recipes, "..\\Data\demo_recipes.json")
        loaded = parser.load_recipes_from_json("demo_recipes.json")
        print(f"\nRe-loaded {len(loaded)} recipes from JSON. Example entries:\n", loaded[:2])

    # 4) Do a quick search for "Pizza" recipes (only page s0)
    print("\n[DEMO] Searching for 'Pizza' recipes (only page 0)...")
    pizza_results = api.searchRecipes("Pizza", end_index=0)
    print(f"Found {len(pizza_results)} pizza recipes. Example:\n", pizza_results[:2])
