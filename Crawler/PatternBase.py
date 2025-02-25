from abc import ABC, abstractmethod


class PatternBase(ABC):
    
    def reset(self):
        self.content = ""
        self.state = 0
    
    def __init__(self, entityFactory):
        self.entityFactory = entityFactory
        self.reset()

    # This is where patterns change their state
    @abstractmethod
    def check_pattern(self, character):
        pass
    
    #workaround for unicode characters
    def check_unicode(self, character):
        if(character == '\\'):
            self.trackingUnicode = True
        if(self.trackingUnicode):
            self.unicodeBuffer += character
            if len(self.unicodeBuffer) == 4:
                try:
                    character = chr(int(self.unicodeBuffer, 16))
                    return character
                except ValueError:
                    self.reset()
                    return None
                self.trackingUnicode = False
            else:
                return None
        
    def check_character(self, character)->str:
        
        unicodeCharacter = self.check_unicode(character)
        if(unicodeCharacter):
            character = unicodeCharacter
        if self.check_pattern(character):
            self.content += character
            if self.state == -1:
                result = self.content
                self.reset()
                return result
            else:
                return ""
        else:
            self.reset()
            return ""
    
    @property
    def InternalState(self)->bool:
        return self.state

    @property
    def Content(self):
        return self.content