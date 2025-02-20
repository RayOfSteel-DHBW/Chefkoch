import requests
from bs4 import BeautifulSoup
import json
import csv
import os


class Category:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Category(name={self.name}, url={self.url})"


class Ingredient:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

    def getName(self):
        return self.name

    def getAmount(self):
        return self.amount

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Ingredient(name={self.name}, amount={self.amount})"


class Tag:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Tag(name={self.name}, url={self.url})"


class Recipe:
    def __init__(self, name, url, ingredients, category, tags=None):
        self.name = name
        self.url = url
        self.ingredients = ingredients
        self.category = category
        self.tags = tags if tags is not None else []

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def getIngredients(self):
        return self.ingredients

    def getCategory(self):
        return self.category

    def getTags(self):
        return self.tags

    def __str__(self):
        return self.name

    def __repr__(self):
        return (f"Recipe(name={self.name}, url={self.url}, "
                f"ingredients={self.ingredients}, category={self.category}, tags={self.tags})")


class ChefkochAPI:
    def __init__(self):
        self.baseURL = "https://www.chefkoch.de"

    def beautifyText(self, text):
        """
        Removes newlines/tabs, multiple spaces, and trims
        """
        text = text.replace("\r", "").replace("\n", "").replace("\t", "")
        # Remove multiple whitespaces
        while "  " in text:
            text = text.replace("  ", " ")
        return text.strip()

    def getCategories(self):
        """
        Fetches categories from https://www.chefkoch.de/rezepte/kategorien/
        and returns them as a list of Category objects.
        """
        url = self.baseURL + "/rezepte/kategorien/"
        resp = requests.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        categories = []

        # The original code looks for div.category-column -> a
        columns = soup.find_all("div", class_="category-column")
        for col in columns:
            links = col.find_all("a")
            for link in links:
                href = link.get("href")
                if not href or href == "#":
                    continue
                name = self.beautifyText(link.get_text())
                categories.append(Category(name, href))
        return categories

    def getCategory(self, categorySubURL):
        """
        Given a relative category URL, fetch its name
        (e.g. for building a Category object).
        """
        full_url = self.baseURL + categorySubURL
        resp = requests.get(full_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        # e.g. the <h1> might be "Pizza Rezepte"
        h1 = soup.find("h1")
        if not h1:
            return None
        text = self.beautifyText(h1.get_text())
        # Chefkoch often has "X Rezepte" after category name. We remove that part:
        if " Rezepte" in text:
            text = text.split(" Rezepte")[0].strip()
        return Category(text, categorySubURL)

    def getRecipe(self, recipeSubURL):
        """
        Fetch full info for a single recipe, given its sub-URL.
        """
        full_url = self.baseURL + recipeSubURL
        resp = requests.get(full_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        h1 = soup.find("h1")
        recipe_name = self.beautifyText(h1.get_text()) if h1 else "No recipe name"

        ingredient_list = []
        table = soup.find("table", class_="ingredients")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                # Right column text
                right_td = row.find("td", class_="td-right")
                left_td = row.find("td", class_="td-left")
                if right_td:
                    ingredient_name = self.beautifyText(right_td.get_text())
                else:
                    ingredient_name = "No ingredient name found"
                if left_td:
                    ingredient_amount = self.beautifyText(left_td.get_text())
                else:
                    ingredient_amount = "No ingredient amount found"

                ingredient_list.append(Ingredient(ingredient_name, ingredient_amount))

        # Category extraction from breadcrumbs
        category = None
        breadcrumb = soup.find("ol", class_="ds-col-12")
        if breadcrumb:
            li_items = breadcrumb.find_all("li")
            # The original code used the 4th <li> (index 3) as the category
            if len(li_items) > 3:
                category_link = li_items[3].find("a")
                if category_link and category_link.get("href"):
                    category_sub_url = category_link["href"]
                    category = self.getCategory(category_sub_url)

        # Tags
        tags_list = []
        tag_div = soup.find("div", class_="recipe-tags")
        if tag_div:
            tag_links = tag_div.find_all("a")
            for t in tag_links:
                t_name = self.beautifyText(t.get_text())
                t_href = t.get("href") or "none"
                tags_list.append(Tag(t_name, t_href))
        else:
            tags_list.append(Tag("No tags found", "none"))

        return Recipe(recipe_name, recipeSubURL, ingredient_list, category, tags_list)

    def getRecipes(self, category, endIndex=5, startIndex=0):
        """
        Iterates from startIndex to endIndex.  
        Replaces '/s0/' with '/s{i}/' in the category URL, fetches recipes.
        """
        # For safety, let’s store the original URL, so we don’t repeatedly
        # replace parts of `category.url` in each loop iteration:
        original_url = category.url
        recipes = []

        for i in range(startIndex, endIndex + 1):
            # Replace '/s0/' with '/s{i}/' or fallback if the category has no 's0' pattern
            modified_url = original_url.replace("/s0/", f"/s{i}/")

            full_url = self.baseURL + modified_url
            resp = requests.get(full_url)
            # If status != 200, this might throw. Usually you'd do `resp.raise_for_status()`
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            # Find recipe cards
            recipe_cards = soup.find_all("div", class_="ds-recipe-card")

            for card in recipe_cards:
                h3 = card.find("h3")
                if not h3:
                    continue
                card_name = self.beautifyText(h3.get_text())

                link_tag = card.find("a")
                if not link_tag:
                    continue
                # The original code splits by '#' to remove anchors
                recipe_url = link_tag.get("href").split("#")[0]

                # Now fetch the individual recipe details
                recipe_obj = self.getRecipe(recipe_url)
                # We want to override the category with the one we know
                recipe_obj.category = category
                # But keep the name we found
                recipe_obj.name = card_name

                recipes.append(recipe_obj)

        return recipes

    def getAllRecipes(self, endIndex=5, startIndex=0):
        """
        Fetches all categories, then fetches recipes for each category.
        Potentially large operation if endIndex is big!
        """
        all_recipes = []
        categories = self.getCategories()
        for cat in categories:
            cat_recipes = self.getRecipes(cat, endIndex=endIndex, startIndex=startIndex)
            all_recipes.extend(cat_recipes)
        return all_recipes

    def searchRecipes(self, query, endIndex=5, startIndex=0):
        """
        Search by query, iterating from start to end. For each ds-recipe-card found,
        fetch the full recipe details.
        """
        recipes = []
        for i in range(startIndex, endIndex + 1):
            search_url = f"{self.baseURL}/rs/s{i}/{query}/Rezepte.html"
            resp = requests.get(search_url)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            recipe_cards = soup.find_all("div", class_="ds-recipe-card")
            for card in recipe_cards:
                h3 = card.find("h3")
                if not h3:
                    continue
                name = self.beautifyText(h3.get_text())

                link_tag = card.find("a")
                if not link_tag:
                    continue
                recipe_url = link_tag.get("href").split("#")[0]

                # For each recipe, fetch details:
                recipe_obj = self.getRecipe(recipe_url)
                # Keep the card name if it differs:
                recipe_obj.name = name
                recipes.append(recipe_obj)

        return recipes


class DataParser:
    def writeFile(self, fileName, data):
        """
        Write raw text data to file.
        """
        with open(fileName, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"The file {fileName} has been saved!")

    def readFile(self, fileName):
        """
        Read raw text data from file.
        """
        with open(fileName, "r", encoding="utf-8") as f:
            return f.read()

    def writeRecipesToJson(self, recipes, fileName):
        """
        Serialize recipes to JSON.
        Since the objects are custom classes, we’ll convert them to dictionaries.
        """
        dict_list = []
        for r in recipes:
            dict_list.append({
                "name": r.getName(),
                "url": r.getUrl(),
                "ingredients": [
                    {"name": ing.getName(), "amount": ing.getAmount()}
                    for ing in r.getIngredients()
                ],
                "category": {
                    "name": r.getCategory().getName() if r.getCategory() else "",
                    "url": r.getCategory().getUrl() if r.getCategory() else ""
                },
                "tags": [
                    {"name": t.getName(), "url": t.getUrl()} for t in r.getTags()
                ]
            })
        json_data = json.dumps(dict_list, ensure_ascii=False, indent=2)
        self.writeFile(fileName, json_data)

    def writeCategoriesToJson(self, categories, fileName):
        dict_list = []
        for c in categories:
            dict_list.append({"name": c.getName(), "url": c.getUrl()})
        json_data = json.dumps(dict_list, ensure_ascii=False, indent=2)
        self.writeFile(fileName, json_data)

    def writeRecipesToCSV(self, recipes, fileName):
        """
        Write minimal CSV: name, url, category name
        """
        with open(fileName, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["RecipeName", "URL", "CategoryName"])
            for r in recipes:
                writer.writerow([r.getName(), r.getUrl(), r.getCategory()])

        print(f"The file {fileName} has been saved in CSV format!")

    def writeCategoriesToCSV(self, categories, fileName):
        with open(fileName, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["CategoryName", "URL"])
            for c in categories:
                writer.writerow([c.getName(), c.getUrl()])
        print(f"The file {fileName} has been saved in CSV format!")

    def loadRecipesFromJson(self, fileName):
        """
        Reads the JSON file, returns a list of dicts or reconstructs them as needed.
        """
        data = self.readFile(fileName)
        items = json.loads(data)
        # If you want to rehydrate them into Recipe objects, do it here:
        recipes = []
        for item in items:
            ing_objs = [
                Ingredient(ing["name"], ing["amount"])
                for ing in item["ingredients"]
            ]
            cat_dict = item["category"]
            cat_obj = Category(cat_dict["name"], cat_dict["url"])
            tag_objs = [Tag(t["name"], t["url"]) for t in item["tags"]]
            recipe = Recipe(item["name"], item["url"], ing_objs, cat_obj, tag_objs)
            recipes.append(recipe)
        return recipes

    def loadCategoriesFromJson(self, fileName):
        """
        Reads the JSON file, returns list of Category objects.
        """
        data = self.readFile(fileName)
        items = json.loads(data)
        categories = []
        for c in items:
            categories.append(Category(c["name"], c["url"]))
        return categories

    def loadRecipesFromCSV(self, fileName):
        """
        This version is limited since the CSV only had name, url, categoryName.
        We might not be able to restore full details from CSV.
        """
        recipes = []
        with open(fileName, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                name, url, cat_str = row
                # We only stored the category name string, so we’ll create a Category with empty URL
                cat_obj = Category(cat_str, "")
                recipes.append(Recipe(name, url, [], cat_obj, []))
        return recipes

    def loadCategoriesFromCSV(self, fileName):
        """
        Reads the CSV, returns list of Category objects.
        """
        categories = []
        with open(fileName, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                name, url = row
                categories.append(Category(name, url))
        return categories


# Optional: quick usage test
if __name__ == "__main__":
    chefkochAPI = ChefkochAPI()
    parser = DataParser()

    # Example 1: Fetch categories
    print("Fetching categories...")
    cats = chefkochAPI.getCategories()
    print("Found categories:", cats[:3], "...\n")

    # Example 2: Fetch recipes from the 1st category
    if cats:
        first_cat = cats[0]
        print(f"Fetching recipes for the category: {first_cat}")
        recipes = chefkochAPI.getRecipes(first_cat, endIndex=1, startIndex=0)
        print("Example recipes:", recipes[:2])

        # Save to JSON
        parser.writeRecipesToJson(recipes, "recipes.json")
        # Read them back
        loaded_recipes = parser.loadRecipesFromJson("recipes.json")
        print("Loaded back from JSON:", loaded_recipes[:2])

    # # Example 3: Search for “Pizza” recipes
    # # (Might be slow if endIndex is large)
    # pizza_results = chefkochAPI.searchRecipes("Pizza", endIndex=0)
    # print("Pizza search results:", pizza_results[:2])
