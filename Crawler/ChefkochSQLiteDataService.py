import sqlite3
import re
from typing import List, Optional
from ChefkochRepository import ChefkochRepository
from ChefkochContracts import Category, Recipe, Ingredient, Tag

class ChefkochSQLiteDataService(ChefkochRepository):
    def __init__(self, db_path: str = r"..\Data\chefkochDB.sqlite") -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT,
            last_page INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            name TEXT NOT NULL,
            amount TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
        );
        """)
        self.conn.commit()

    def category_exists(self, category_name: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories WHERE name = ?", (category_name,))
        count = cursor.fetchone()[0]
        return count > 0

    def save_category(self, category: Category) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO categories (name, url, last_page) VALUES (?, ?, ?)",
                       (category.name, category.url, 0))
        self.conn.commit()

    def get_category_page(self, category_name: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT last_page FROM categories WHERE name = ?", (category_name,))
        row = cursor.fetchone()
        if row is None:
            return 0
        return row[0] if row[0] else 0

    def update_category_page(self, category_name: str, page: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("UPDATE categories SET last_page = ? WHERE name = ?", (page, category_name))
        self.conn.commit()

    def recipe_exists(self, recipe_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE id = ?", (recipe_id,))
        count = cursor.fetchone()[0]
        return count > 0

    def save_recipe(self, recipe: Recipe) -> None:
        if not recipe.category:
            category_id = None
        else:
            self.save_category(recipe.category)
            category_id = self._get_category_id(recipe.category.name)
        recipe_id = self._extract_recipe_id(recipe.url)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO recipes (id, name, url, category_id)
            VALUES (?, ?, ?, ?)
        """, (recipe_id, recipe.name, recipe.url, category_id))
        self.conn.commit()

    def save_ingredients(self, recipe_id: str, ingredients: List[Ingredient]) -> None:
        cursor = self.conn.cursor()
        for ing in ingredients:
            cursor.execute("""
                INSERT INTO ingredients (recipe_id, name, amount)
                VALUES (?, ?, ?)
            """, (recipe_id, ing.name, ing.amount))
        self.conn.commit()

    def save_tags(self, recipe_id: str, tags: List[Tag]) -> None:
        cursor = self.conn.cursor()
        for t in tags:
            cursor.execute("""
                INSERT INTO tags (recipe_id, name, url)
                VALUES (?, ?, ?)
            """, (recipe_id, t.name, t.url))
        self.conn.commit()

    def _get_category_id(self, category_name: str) -> Optional[int]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def _extract_recipe_id(self, recipe_url: str) -> str:
        match = re.search(r"/rezepte/(\d+)", recipe_url)
        return match.group(1) if match else recipe_url

    def _get_ingredients_for_recipe(self, recipe_id: str) -> List[Ingredient]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, amount FROM ingredients WHERE recipe_id = ?
        """, (recipe_id,))
        rows = cursor.fetchall()
        return [Ingredient(name=row[0], amount=row[1]) for row in rows]

    def _get_tags_for_recipe(self, recipe_id: str) -> List[Tag]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, url FROM tags WHERE recipe_id = ?
        """, (recipe_id,))
        rows = cursor.fetchall()
        return [Tag(name=row[0], url=row[1]) for row in rows]
    
    def initialize_categories(self, categories: List[Category]) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        if count == 0:
            for cat in categories:
                self.save_category(cat)