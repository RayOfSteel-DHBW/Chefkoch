from peewee import Model, CharField, IntegerField, ManyToManyField, ForeignKeyField

from ChefkochContracts import Category

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
    
    def ToDomainObject(self)->Category:
        return Category(self.name, self.url, self.external_id, self.current_page, self.max_page)
        

class RecipeModel(ChefkochEntityModel):
    ingredients = ManyToManyField(IngredientModel, backref='recipes')
    categories = ManyToManyField(CategoryModel, backref='recipes')

RecipeIngredient = RecipeModel.ingredients.get_through_model()
RecipeCategory = RecipeModel.categories.get_through_model()
