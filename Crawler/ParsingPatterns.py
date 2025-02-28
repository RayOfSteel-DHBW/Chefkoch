from PatternBase import PatternBase
from ChefkochModels import IngredientModel, CategoryModel, RecipeModel

class CategoryTagPattern(PatternBase):
    def __init__(self):
        self.tagStart = '<a href="/rs/s'
        self.classMarker = 'class="ds-tag bi-tags"'
        super().__init__()
        
    def reset(self):
        super().reset()
        self.state = 0
        self.tagBuffer = ""
        self.urlBuffer = ""
        self.nameBuffer = ""
        self.idBuffer = ""
        self.extractingName = False
        
    def check_pattern(self, character):
        # State 0: Looking for start of anchor tag with href
        if self.state == 0:
            self.tagBuffer += character
            if len(self.tagBuffer) > len(self.tagStart):
                self.tagBuffer = self.tagBuffer[1:]  # Keep buffer size manageable
            if self.tagBuffer.endswith(self.tagStart):
                self.urlBuffer = "/rs/s"
                self.state = 1  # Found opening of anchor tag, now collect s-number
                return True
             
        elif self.state == 1:
            # Existing code
            self.urlBuffer += character
            if character == '/':
                id_part = self.urlBuffer.split('/')[-2]
                if 't' in id_part:
                    self.idBuffer = id_part.split('t')[-1]
                else:
                    self.idBuffer = ''.join(c for c in id_part if c.isdigit())
                self.state = 2
                return True
            return True
                
        elif self.state == 2:
            # Existing code
            self.tagBuffer += character
            if len(self.tagBuffer) > len(self.classMarker):
                self.tagBuffer = self.tagBuffer[1:]
            if self.tagBuffer.endswith(self.classMarker):
                self.state = 3
                return True
            return True
            
        elif self.state == 3:
            # Existing code
            if character == '>':
                self.extractingName = True
                self.state = 4
                return True
            return True
            
        elif self.state == 4:
            # Existing code
            if character == '<':
                self.extractingName = False
                self.state = 5
                self.tagBuffer = character
                return True
            if self.extractingName:
                self.nameBuffer += character
            return True
            
        # In state 5, update the entity's categories
        elif self.state == 5:
            self.tagBuffer += character
            if self.tagBuffer == "</a>":
                name = self.nameBuffer.strip()
                url = self.urlBuffer
                
                try:
                    category_id = int(self.idBuffer)
                    category = CategoryModel(name=name, url=url, external_id=category_id)
                    
                    # Add category to the recipe's categories
                    if self.result and isinstance(self.result.entity, RecipeModel):
                        self.result.entity.categories.append(category)
                        # Also add to foundCategories for crawling
                        self.result.foundCategories.append(url)
                        
                    self.state = -1
                except ValueError:
                    self.reset()
                
                return True
            return True
            
        return False

class IngredientTablePattern(PatternBase):
    def __init__(self):
        self.tableStartTag = '<table class="ingredients table-header"'
        self.fixedEnd = '</table>'
        super().__init__()
        
    def reset(self):
        super().reset()
        self.state = 0
        self.currentTag = ""
        self.inTable = False
        self.inRow = False
        self.inLeftCell = False
        self.inRightCell = False
        self.amount = ""
        self.name = ""
        self.htmlBuffer = ""
        self.tableBuffer = ""
        self.tagBuffer = ""
        self.extractMode = False
        
    def check_pattern(self, character):
        # States 0-1 remain unchanged
        if self.state == 0:
            self.tableBuffer += character
            if len(self.tableBuffer) > len(self.tableStartTag):
                self.tableBuffer = self.tableBuffer[1:]
            
            if self.tableBuffer.endswith(self.tableStartTag):
                self.state = 1
                self.inTable = True
                return True
                
        elif self.state == 1:
            if character == '<':
                self.tagBuffer = character
                self.state = 2
                return True
            return True
            
        # Handle row endings to create ingredients
        elif self.state == 2:
            self.tagBuffer += character
            
            if self.tagBuffer.endswith('td-left'):
                self.inLeftCell = True
                self.inRightCell = False
                self.state = 3
                return True
                
            elif self.tagBuffer.endswith('td-right'):
                self.inLeftCell = False
                self.inRightCell = True
                self.state = 4
                return True
                
            elif self.tagBuffer.endswith('</tr>'):
                if self.name:
                    ingredient = IngredientModel(name=self.name.strip())
                    
                    # Add ingredient to the recipe's ingredients
                    if self.result and isinstance(self.result.entity, RecipeModel):
                        self.result.entity.ingredients.append(ingredient)
                        
                    self.amount = ""
                    self.name = ""
                self.state = 1
                return True
                
            elif self.tagBuffer.endswith(self.fixedEnd):
                self.state = -1
                return True
                
            return True
            
        # States 3-6 remain unchanged
        elif self.state == 3:
            if character == '<':
                self.tagBuffer = character
                self.state = 5
                return True
            if self.extractMode:
                self.amount += character
            return True
            
        elif self.state == 4:
            if character == '<':
                self.tagBuffer = character
                self.state = 6
                return True
            if self.extractMode:
                self.name += character
            return True
            
        elif self.state == 5:
            self.tagBuffer += character
            if self.tagBuffer.endswith('<span>'):
                self.extractMode = True
                self.state = 3
                return True
            elif self.tagBuffer.endswith('</span>'):
                self.extractMode = False
                self.state = 3
                return True
            elif self.tagBuffer.endswith('</td>'):
                self.inLeftCell = False
                self.state = 1
                return True
            return True
            
        elif self.state == 6:
            self.tagBuffer += character
            if self.tagBuffer.endswith('<span>'):
                self.extractMode = True
                self.state = 4
                return True
            elif self.tagBuffer.endswith('</span>'):
                self.extractMode = False
                self.state = 4
                return True
            elif self.tagBuffer.endswith('</td>'):
                self.inRightCell = False
                self.state = 1
                return True
            return True
            
        return False

class CategoryPattern(PatternBase):
    def __init__(self):
        self.fixedStart = "rs/"
        self.fixedEnd = "html"
        self.reset()

    def reset(self):
        super().reset()
        self.state = 0
        self.htmlBuffer = ""

    def check_pattern(self, character):
        if self.state == 0:
            self.content += character
            if self.fixedStart[len(self.content)] == character:
                if len(self.content) == len(self.fixedStart):
                    self.state = 1
                    return True
        elif self.state == 1:
            if character.isalnum():
                self.content += character
                self.state = 2
                return True
        elif self.state == 2:
            if character == '/' or character.isalnum() or character == '-':
                self.content += character
                if character == '.':
                    self.state = 3
                return True
        elif self.state == 3:
            if len(self.htmlBuffer) < 4:
                self.htmlBuffer += character
                if len(self.htmlBuffer) == 4:
                    if self.htmlBuffer == self.fixedEnd:
                        self.content += self.htmlBuffer
                        self.state = -1
                        return True
                    else:
                        self.reset()
                        return False
                return True
        # When we reach the end state
        elif self.state == -1:
            # Add URL to foundCategories for crawling
            if self.result and self.content:
                self.result.foundCategories.append(self.content)
            return True
        else:
            self.reset()
        return False

class RezeptePattern(PatternBase):
    def __init__(self):
        self.fixedStart = "rezepte"
        self.fixedEnd = "html"
        super().__init__()

    def reset(self):
        super().reset()
        self.state = 0
        self.htmlBuffer = ""

    def check_pattern(self, character, result):
        if self.state == 0:
            if(self.fixedStart[len(self.content)] == character):
                self.content += character
                if len(self.content) == len(self.fixedStart):
                    self.state = 1
                    return True
        elif self.state == 1:
            if(character.isdigit()):
                self.idBuffer += character
                if len(self.idBuffer) == 15:
                    self.content += self.idBuffer
                    self.state = 2
                return True
        elif self.state == 2:
            if(character == '/'):
                self.content += character
                self.state = 3
                return True
        elif self.state == 3:
            if(character.isalnum() or character == '-'):
                self.content += character
                self.fileNameBuffer += character
            elif(character == '.'):
                self.content += character
                self.state = 4
                return True
        elif self.state == 4:
            if(self.htmlBuffer < 4):
                self.htmlBuffer += character
                return True
            if(self.htmlBuffer == self.fixedEnd):
                self.content += self.htmlBuffer
                result.foundRecipes.append(self.content)
                return False
            return True
        return False

class RecipeTitlePattern(PatternBase):
    def __init__(self):
        self.titleStart = '<h1 class="ds-h1"'
        self.titleEnd = '</h1>'
        super().__init__()
        
    def reset(self):
        super().reset()
        self.state = 0
        self.tagBuffer = ""
        self.nameBuffer = ""
        self.extractingName = False
        
    def check_pattern(self, character):
        # State 0: Looking for start of title tag
        if self.state == 0:
            self.tagBuffer += character
            if len(self.tagBuffer) > len(self.titleStart):
                self.tagBuffer = self.tagBuffer[1:]  # Keep buffer size manageable
            if self.tagBuffer.endswith(self.titleStart):
                self.state = 1  # Found opening of title tag
                return True
                
        # State 1: Looking for end of opening tag (>)
        elif self.state == 1:
            if character == '>':
                self.extractingName = True
                self.state = 2  # Start extracting recipe name
                return True
            return True
            
        # State 2: Collecting recipe name
        elif self.state == 2:
            if character == '<':
                self.extractingName = False
                self.state = 3  # Check for closing tag
                self.tagBuffer = character
                return True
            if self.extractingName:
                self.nameBuffer += character
            return True
            
        # In state 3, update the recipe name
        elif self.state == 3:
            self.tagBuffer += character
            if self.tagBuffer == self.titleEnd:
                recipe_name = self.nameBuffer.strip()
                # Update the name of the entity
                if recipe_name and self.result and self.result.entity:
                    self.result.entity.name = recipe_name
                self.state = -1
                return True
            return True
            
        return False
