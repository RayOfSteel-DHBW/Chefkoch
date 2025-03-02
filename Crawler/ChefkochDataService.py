from ast import Tuple
from pathlib import Path
from peewee import (
    Model, CharField, IntegerField, ManyToManyField, SqliteDatabase,
    DoesNotExist, ForeignKeyField
)
from typing import Union

db_path = Path(r'Data\crawled_data.db').resolve()
db = SqliteDatabase(str(db_path), pragmas={'journal_mode': 'wal'})


class ChefkochObjectModel(Model):
    name = CharField()
    class Meta:
        database = db
        abstract = True


class ChefkochEntityModel(ChefkochObjectModel):
    file = CharField()

    @property
    def url(self):
        raise NotImplementedError("Subclasses must implement url property")

    class Meta:
        abstract = True


class IngredientModel(ChefkochObjectModel):
    # Use a separate field for the amount. If an ingredient can appear multiple times
    # with different amounts, consider storing that in the through-table only.
    pass


class CategoryModel(ChefkochEntityModel):
    category_id = IntegerField()
    current_page = IntegerField(default=0)
    max_page = IntegerField(default=1)

    @property
    def url(self):
        return f"https://www.chefkoch.de/rs/s{self.current_page}t{self.category_id}/{self.file}"

    @property
    def next_page_url(self):
        if self.current_page < self.max_page:
            return f"https://www.chefkoch.de/rs/s{self.current_page + 1}t{self.category_id}/{self.file}"
        else:
            return f"https://www.chefkoch.de/rs/s{self.max_page}t{self.category_id}/{self.file}"


class RecipeModel(ChefkochEntityModel):
    categories = ManyToManyField(CategoryModel, backref='recipes')
    recipe_id = CharField()

    @property
    def url(self):
        return f"https://www.chefkoch.de/rezepte/{self.recipe_id}/{self.file}"
    
class RecipeIngredientThroughModel(Model):
    recipe = ForeignKeyField(RecipeModel, backref='recipe_ingredients')
    ingredient = ForeignKeyField(IngredientModel, backref='ingredient_recipes')
    amount = CharField()

    class Meta:
        database = db

RecipeCategoryThrough = RecipeModel.categories.get_through_model()


class ChefkochDataService:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([
            IngredientModel,
            CategoryModel,
            RecipeModel,
            RecipeIngredientThroughModel,
            RecipeCategoryThrough
        ], safe=True)

    def create_or_update_category(self, category_data: CategoryModel) -> CategoryModel:
        """
        Check if a category already exists by (name, category_id).
        If it does, update current_page and max_page.
        If not, create a new one.
        """
        with db.atomic():
            category, created = CategoryModel.get_or_create(
                name=category_data.name,
                category_id=category_data.category_id,
                file=category_data.file,
                defaults={
                    'current_page': category_data.current_page,
                    'max_page': category_data.max_page
                }
            )
            if not created:
                # If the category already exists, update it as needed
                category.current_page = category_data.current_page
                category.max_page = category_data.max_page
                category.file = category_data.file
                category.save()
                print(f"[UPDATED Category] {category.name} (ID: {category.category_id}, current_page: {category.current_page}, max_page: {category.max_page})")
            else:
                print(f"[CREATED Category] {category.name} (ID: {category.category_id}, current_page: {category.current_page}, max_page: {category.max_page})")

            return category

    def create_or_update_recipe(self, recipe_data: RecipeModel, ingredients: dict[str, str]) -> RecipeModel:
        # Wrap the whole operation in a transaction to ensure atomicity.
        with db.atomic():
            # Either fetch an existing recipe or create a new one
            recipe, created = RecipeModel.get_or_create(
                name=recipe_data.name,
                recipe_id=recipe_data.recipe_id,
                defaults={'file': recipe_data.file}
            )
            if not created:
                # If the recipe already exists, update fields as needed
                recipe.file = recipe_data.file
                recipe.save()
                print(f"[UPDATED Recipe] {recipe.name} (ID: {recipe.recipe_id})")
            else:
                print(f"[CREATED Recipe] {recipe.name} (ID: {recipe.recipe_id})")

            # Process and link ingredients with the custom through model.
            for ingredientName, ingredientAmount in ingredients.items():
                ingredient, ing_created = IngredientModel.get_or_create(name=ingredientName)
                if ing_created:
                    print(f"   -> [CREATED Ingredient] {ingredient.name}")
                else:
                    print(f"   -> [FOUND Ingredient] {ingredient.name}")

                # Create or update the link in the through model.
                recipe_ing, thr_created = RecipeIngredientThroughModel.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    defaults={'amount': ingredientAmount}
                )
                if not thr_created:
                    # Update the amount if the link already exists.
                    recipe_ing.amount = ingredientAmount
                    recipe_ing.save()

                print(f"      - Linked: {ingredient.name} with amount {ingredientAmount}")

            # Process and link categories
            for cat_id in recipe_data.categories:
                try:
                    cat = CategoryModel.get_by_id(cat_id)
                    recipe.categories.add(cat)
                    print(f"   -> Linked Recipe '{recipe.name}' with Category '{cat.name}' (ID: {cat.category_id})")
                except DoesNotExist:
                    print(f"   -> [WARNING] Category with ID {cat_id} does not exist.")
            
            return recipe

    def process_entity(self, entity: ChefkochEntityModel, ingredients:dict[str, str]) -> None:
        """
        General method to process an entity.
        If it's a CategoryModel, create or update it.
        If it's a RecipeModel, create or update it with its related data.
        """
        if isinstance(entity, CategoryModel):
            if(entity.current_page < entity.max_page):
                entity.current_page += 1
            self.create_or_update_category(entity)
        elif isinstance(entity, RecipeModel):
            self.create_or_update_recipe(entity, ingredients)
        else:
            raise ValueError("Unsupported entity type")
        db.commit()

    def get_categories_for_update(self):
        """
        Returns categories that can still be updated (i.e., current_page < max_page).
        """
        return CategoryModel.select().where(CategoryModel.current_page < CategoryModel.max_page)
