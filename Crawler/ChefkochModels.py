from peewee import Model, CharField, IntegerField, ManyToManyField, ForeignKeyField

class ChefkochObjectModel(Model):
    name = CharField()

    class Meta:
        database = None
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
    max_page = IntegerField(default=0)

class RecipeModel(ChefkochEntityModel):
    ingredients = ManyToManyField(IngredientModel, backref='recipes')
    categories = ManyToManyField(CategoryModel, backref='recipes')

RecipeIngredient = RecipeModel.ingredients.get_through_model()
RecipeCategory = RecipeModel.categories.get_through_model()
