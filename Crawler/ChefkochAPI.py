import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from ChefkochContracts import Category, Ingredient, Recipe, Tag

class ChefkochAPI:
    def __init__(self) -> None:
        self.base_url = "https://www.chefkoch.de"
        

    def beautify_text(self, text: str) -> str:
        text = text.replace("\r", "").replace("\n", "").replace("\t", "")
        while "  " in text:
            text = text.replace("  ", " ")
        return text.strip()

    def _find_category_by_name(self, cat_name: str) -> Optional[Category]:
        for c in self.getCategories():
            if c.name.lower() == cat_name.lower():
                return c
        return None

    def get_recipe(self, recipe_sub_url: str) -> Recipe:
        if recipe_sub_url.startswith("http"):
            full_url = recipe_sub_url
        else:
            full_url = self.base_url + recipe_sub_url

        resp = requests.get(full_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        h1 = soup.find("h1")
        recipe_name = self.beautify_text(h1.get_text()) if h1 else "No recipe name"

        ingredient_list: List[Ingredient] = []
        table = soup.find("table", class_="ingredients")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                right_td = row.find("td", class_="td-right")
                left_td = row.find("td", class_="td-left")
                ing_name = self.beautify_text(right_td.get_text()) if right_td else "No ingredient name"
                ing_amount = self.beautify_text(left_td.get_text()) if left_td else "No amount"
                ingredient_list.append(Ingredient(name=ing_name, amount=ing_amount))

        category_obj = None
        breadcrumb = soup.find("ol", class_="ds-col-12")
        if breadcrumb:
            li_items = breadcrumb.find_all("li")
            if len(li_items) > 3:
                cat_link = li_items[3].find("a")
                if cat_link and cat_link.get("href"):
                    category_sub_url = cat_link["href"]
                    category_obj = self._derive_category_from_suburl(category_sub_url)

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

    def _derive_category_from_suburl(self, category_sub_url: str) -> Optional[Category]:
        full_url = self.base_url + category_sub_url
        resp = requests.get(full_url)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        h1 = soup.find("h1")
        if not h1:
            return None
        text = self.beautify_text(h1.get_text())
        if " Rezepte" in text:
            text = text.split(" Rezepte")[0].strip()
        return Category(name=text, url=category_sub_url)

    def getRecipes_for_page(self, category_name: str, page_index: int) -> List[Recipe]:
        cat = self._find_category_by_name(category_name)
        if not cat:
            return []
        page_url = cat.url.replace("/s0t", f"/s{page_index}t")
        resp = requests.get(page_url)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        recipe_cards = soup.find_all("div", class_="ds-recipe-card")

        collected: List[Recipe] = []
        for card in recipe_cards:
            h3 = card.find("h3")
            if not h3:
                continue
            card_name = self.beautify_text(h3.get_text())
            link_tag = card.find("a")
            if not link_tag:
                continue
            recipe_sub_url = link_tag.get("href").split("#")[0]
            recipe_obj = self.get_recipe(recipe_sub_url)
            recipe_obj.category = cat
            recipe_obj.name = card_name
            collected.append(recipe_obj)
        return collected
