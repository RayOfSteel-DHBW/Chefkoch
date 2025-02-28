from abc import ABC, abstractmethod


class PatternBase(ABC):
    
    def reset(self):
        self.content = ""
        self.state = 0
        self.trackingUnicode = False
        self.unicodeBuffer = ""
    
    def __init__(self):
        self.reset()

    # This is where patterns change their state
    @abstractmethod
    def check_pattern(self, character, parsingResult):
        raise NotImplementedError("Subclasses must implement this method")
    #workaround for unicode characters
    def check_unicode(self, character):
        if(character == '\\'):
            self.trackingUnicode = True
        if(self.trackingUnicode):
            if(len(self.unicodeBuffer) == 1):
                if(character != 'u'):
                    self.reset()
                    return None
            self.unicodeBuffer += character
            if len(self.unicodeBuffer) == 4:
                try:
                    character = chr(int(self.unicodeBuffer, 16))
                    return character
                except ValueError:
                    self.reset()
                    return None
            else:
                return None
        
    def check_character(self, character, parsingResult):
        unicodeCharacter = self.check_unicode(character)
        if(unicodeCharacter):
            character = unicodeCharacter
        try:
            if self.check_pattern(character, parsingResult):
                self.content += character
            else:
                self.reset()
        except Exception as e:
            self.reset()
            print(f"An error occurred: {e}")
        return parsingResult