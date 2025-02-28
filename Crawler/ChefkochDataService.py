from peewee import Model, CharField, IntegerField, ManyToManyField, SqliteDatabase
from pathlib import Path

db_path = Path(Path(r'..\Data\crawled_data.db').resolve())
# Ensure the data directory exists

# Initialize database
db = SqliteDatabase(str(db_path), pragmas={'journal_mode': 'wal'})

class ChefkochObjectModel(Model):
    name = CharField()
    class Meta:
        database = db
        abstract = True

class ChefkochEntityModel(ChefkochObjectModel):
    url = CharField(null=True)
    class Meta:
        abstract = True

class IngredientModel(ChefkochObjectModel):
    amount = CharField()

class CategoryModel(ChefkochEntityModel):
    chefkoch_id = IntegerField()
    current_page = IntegerField(default=0)
    max_page = IntegerField(default=1)

class RecipeModel(ChefkochEntityModel):
    ingredients = ManyToManyField(IngredientModel, backref='recipes')
    categories = ManyToManyField(CategoryModel, backref='recipes')

RecipeIngredient = RecipeModel.ingredients.get_through_model()
RecipeCategory = RecipeModel.categories.get_through_model()

class ChefkochDataService:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([IngredientModel, CategoryModel, RecipeModel, RecipeModel.ingredients.get_through_model(), RecipeModel.categories.get_through_model()], safe=True)
        
    def create_entity(self, entity, is_recipe):
        with db.atomic():  # context manager to avoid half finished entries
            if is_recipe:
                recipe = RecipeModel.create(name=entity.name, url=entity.url)
                recipe.save()
                
                for ingredient in entity.ingredients:
                    ingredient_model, created = IngredientModel.get_or_create(name=ingredient.name)
                    recipe.ingredients.add(ingredient_model, through_defaults={'amount': ingredient.amount})
                for category in entity.categories:
                    category_model, created = CategoryModel.get_or_create(name=category.name, external_id=category.external_id)
                    recipe.categories.add(category_model)
            else:
                CategoryModel.create(
                    name=entity.name,
                    url=entity.url,
                    external_id=entity.external_id)

    def get_categories(self):
        return CategoryModel.select().where(CategoryModel.current_page < CategoryModel.max_page)
