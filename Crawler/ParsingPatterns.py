from PatternBase import PatternBase
from ChefkochContracts import Ingredient

class CategoryTagPattern(PatternBase):
    def __init__(self, entityFactory):
        self.tagStart = '<a href="/rs/s'
        self.classMarker = 'class="ds-tag bi-tags"'
        super().__init__(entityFactory)
        
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
                
        # State 1: Collecting the part after /rs/s (could be 0t21, 123, etc.)
        elif self.state == 1:
            self.urlBuffer += character
            
            # Look for / that indicates end of the ID part
            if character == '/':
                # Extract the ID from the URL (assuming format like s0t123/)
                id_part = self.urlBuffer.split('/')[-2]  # Get the part before the slash
                if 't' in id_part:
                    # Format is like s0t123
                    self.idBuffer = id_part.split('t')[-1]  # Get the number after 't'
                else:
                    # Just get the numeric part
                    self.idBuffer = ''.join(c for c in id_part if c.isdigit())
                
                self.state = 2  # Now look for class attribute
                return True
            return True
                
        # State 2: Look for class attribute
        elif self.state == 2:
            self.tagBuffer += character
            if len(self.tagBuffer) > len(self.classMarker):
                self.tagBuffer = self.tagBuffer[1:]
            if self.tagBuffer.endswith(self.classMarker):
                self.state = 3  # Found class marker, now look for tag end
                return True
            return True
            
        # State 3: Looking for tag end (>)
        elif self.state == 3:
            if character == '>':
                self.extractingName = True
                self.state = 4  # Start extracting category name
                return True
            return True
            
        # State 4: Collecting category name
        elif self.state == 4:
            if character == '<':
                self.extractingName = False
                self.state = 5  # Check for closing tag
                self.tagBuffer = character
                return True
            if self.extractingName:
                self.nameBuffer += character
            return True
            
        # State 5: Verifying </a> closing tag
        elif self.state == 5:
            self.tagBuffer += character
            if self.tagBuffer == "</a>":
                # We have a complete category, create it
                from ChefkochContracts import Category
                
                name = self.nameBuffer.strip()
                url = self.urlBuffer
                
                try:
                    category_id = int(self.idBuffer)
                    category = Category(name, url, category_id)
                    self.entityFactory(category)
                    self.state = -1  # We're done
                except ValueError:
                    # Couldn't parse the ID, reset
                    self.reset()
                
                return True
            return True
            
        return False

class IngredientTablePattern(PatternBase):
    def __init__(self, entityFactory):
        self.tableStartTag = '<table class="ingredients table-header"'
        self.fixedEnd = '</table>'
        super().__init__(entityFactory)
        
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
        # State 0: Looking for table start
        if self.state == 0:
            self.tableBuffer += character
            if len(self.tableBuffer) > len(self.tableStartTag):
                self.tableBuffer = self.tableBuffer[1:]
            
            if self.tableBuffer.endswith(self.tableStartTag):
                self.state = 1  # Found table tag
                self.inTable = True
                return True
                
        # State 1: Inside table, looking for rows
        elif self.state == 1:
            if character == '<':
                self.tagBuffer = character
                self.state = 2  # Start collecting tag
                return True
            return True
            
        # State 2: Collecting tag name
        elif self.state == 2:
            self.tagBuffer += character
            
            # Check for td-left class
            if self.tagBuffer.endswith('td-left'):
                self.inLeftCell = True
                self.inRightCell = False
                self.state = 3  # Now looking for span with amount
                return True
                
            # Check for td-right class
            elif self.tagBuffer.endswith('td-right'):
                self.inLeftCell = False
                self.inRightCell = True
                self.state = 4  # Now looking for ingredient name
                return True
                
            # Check for end of row
            elif self.tagBuffer.endswith('</tr>'):
                # If we have data, create an ingredient
                if self.name:
                    # Create an ingredient using the factory
                    ingredient = Ingredient(self.name.strip(), self.amount.strip())
                    self.entityFactory(ingredient)
                    # Reset for next ingredient
                    self.amount = ""
                    self.name = ""
                self.state = 1
                return True
                
            # Check for end of table
            elif self.tagBuffer.endswith(self.fixedEnd):
                self.state = -1  # We're done
                return True
                
            return True
            
        # State 3: Looking for amount in left cell
        elif self.state == 3:
            if character == '<':
                self.tagBuffer = character
                self.state = 5  # Check what tag this is
                return True
                
            # If we're extracting content, add to amount
            if self.extractMode:
                self.amount += character
                
            return True
            
        # State 4: Looking for ingredient name in right cell
        elif self.state == 4:
            if character == '<':
                self.tagBuffer = character
                self.state = 6  # Check what tag this is
                return True
                
            # If we're extracting content, add to name
            if self.extractMode:
                self.name += character
                
            return True
            
        # State 5: Checking tags in left cell
        elif self.state == 5:
            self.tagBuffer += character
            
            # Start extracting after span open
            if self.tagBuffer.endswith('<span>'):
                self.extractMode = True
                self.state = 3
                return True
                
            # Stop extracting at span close
            elif self.tagBuffer.endswith('</span>'):
                self.extractMode = False
                self.state = 3
                return True
                
            # End of left cell
            elif self.tagBuffer.endswith('</td>'):
                self.inLeftCell = False
                self.state = 1
                return True
                
            return True
            
        # State 6: Checking tags in right cell
        elif self.state == 6:
            self.tagBuffer += character
            
            # Start extracting after span open
            if self.tagBuffer.endswith('<span>'):
                self.extractMode = True
                self.state = 4
                return True
                
            # Stop extracting at span close
            elif self.tagBuffer.endswith('</span>'):
                self.extractMode = False
                self.state = 4
                return True
                
            # End of right cell
            elif self.tagBuffer.endswith('</td>'):
                self.inRightCell = False
                self.state = 1
                return True
                
            return True
            
        return False
class CategoryPattern(PatternBase):
    def __init__(self):
        self.fixedStart = "rs"
        self.fixedEnd = "html"
        super().__init__()

    def reset(self):
        super().reset()
        self.state = 0
        self.htmlBuffer = ""

    def check_pattern(self, character):
        if self.state == 0:
            if self.fixedStart[len(self.content)] == character:
                self.content += character
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
        else:
            self.reset()
            return False
        return True

class RezeptePattern(PatternBase):
    def __init__(self):
        self.fixedStart = "rezepte/"
        super().__init__()

    def reset(self):
        super().reset()
        self.state = 0
        self.numericIndex = 0
        self.idBuffer = ""
        self.fileNameBuffer = ""
        self.htmlBuffer = ""
    
    def check_pattern(self, character):
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
                self.state = -1
                return True
        else:
            return False
