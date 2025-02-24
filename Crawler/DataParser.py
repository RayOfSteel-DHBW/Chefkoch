import csv
import json
import os
from typing import List

from Crawler.ChefkochContracts import Category, Ingredient, Recipe, Tag


class DataParser:
    """
    Handles reading/writing recipes/categories to disk
    in JSON or CSV formats.
    """
    def write_file(self, filename: str, data: str) -> None:
        """Write raw text data to file (UTF-8)."""
        os.makedirs(os.path.dirname(filename),_ok=True)
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
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["RecipeName", "URL", "CategoryName"])
            for r in recipes:
                cat_name = r.category.name if r.category else ""
                writer.writerow([r.name, r.url, cat_name])
        print(f"[INFO] The file '{filename}' has been saved in CSV format.")

    def write_categories_to_csv(self, categories: List[Category], filename: str) -> None:
        """Write categories (name, url) to a CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
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

