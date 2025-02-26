from abc import ABC, abstractmethod


class PatternBase(ABC):
    
    def reset(self):
        self.content = ""
        self.state = 0
        self.trackingUnicode = False
    
    def __init__(self):
        self.reset()

    # This is where patterns change their state
    @abstractmethod
    def check_pattern(self, character):
        raise NotImplementedError("Subclasses must implement this method")
    
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
        
    def check_character(self, character, parsingResult)->str:
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

    def add_entity(self, entity):
        """Add an entity to the collection"""
        self.collected_entities.append(entity)
        
    def get_collected_entities(self):
        """Return and clear the collected entities"""
        entities = self.collected_entities.copy()
        self.collected_entities = []
        return entities