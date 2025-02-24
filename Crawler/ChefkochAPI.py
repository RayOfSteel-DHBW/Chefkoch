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

    def getCategories(self) -> List[Category]:
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
