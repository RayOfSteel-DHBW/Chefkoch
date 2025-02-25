from PatternBase import PatternBase

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
