from peewee import Model, CharField, IntegerField, ManyToManyField, SqliteDatabase
from pathlib import Path
db_path = Path(r'..\Data\crawled_data.db')
# Ensure the data directory exists
 
# Initialize database
db = SqliteDatabase(str(db_path),
                    pragmas={'journal_mode': 'wal'})

def init_tables():
    if not db_path.exists():
        RecipeIngredient = RecipeModel.ingredients.get_through_model()
        RecipeCategory = RecipeModel.categories.get_through_model()

    db.create_tables([IngredientModel, CategoryModel, RecipeModel, 
                     RecipeIngredient, RecipeCategory], safe=True)
    db.connect(reuse_if_open=True)
    
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
    external_id = IntegerField()
    current_page = IntegerField(default=0)
    max_page = IntegerField(default=1)
        

class RecipeModel(ChefkochEntityModel):
    ingredients = ManyToManyField(IngredientModel, backref='recipes')
    categories = ManyToManyField(CategoryModel, backref='recipes')


class ChefkochDataService:
    def create_entity(self, entity, is_recipe):
        with db.atomic():  # Use a context manager to handle the transaction
            if is_recipe:
                # Assuming entity is a RecipeModel instance
                recipe = RecipeModel.create(name=entity.name, url=entity.url)
                for ingredient in entity.ingredients:
                    ingredient_model = IngredientModel.get_or_create(name=ingredient.name)
                    recipe.ingredients.add(ingredient_model, through_defaults={'amount': ingredient.amount})
                for category in entity.categories:
                    category_model = CategoryModel.get_or_create(name=category.name, external_id=category.external_id)
                    recipe.categories.add(category_model)
            else:
                CategoryModel.create(
                    name=entity.name,
                    url=entity.url,
                    external_id=entity.external_id)
            db.commit()

    def get_categories(self):
        return CategoryModel.select().where(CategoryModel.current_page < CategoryModel.max_page)