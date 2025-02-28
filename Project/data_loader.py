import json
import re
import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        # Initialize with the path to the JSON file
        self.filepath = filepath

    def load_data_and_clean(self):
        """
        Loads the JSON data from the given file path and cleans it.
        """
        # Load the JSON data from file
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        
        # Convert the list of recipe dictionaries to a pandas DataFrame
        df = pd.DataFrame(data)
        
        # Define a helper function to parse a single ingredient string.
        def parse_ingredient(ingredient_str):

            pattern = r'^([\d\.\s\/\w]+)\s+(.*)$'
            match = re.match(pattern, ingredient_str)
            if match:
                amount = match.group(1).strip()
                ingredient = match.group(2).strip()
            else:
                amount = ''
                ingredient = ingredient_str.strip()
            return {'amount': amount, 'ingredient': ingredient}
        
        # Function to parse a list of ingredient strings
        def parse_ingredients_list(ingredients):
            return [parse_ingredient(ing) for ing in ingredients]
        
        # Apply parsing to the 'Ingredients' field if it exists
        if 'Ingredients' in df.columns:
            # Create a new column with the parsed ingredients for more granular analysis
            df['ParsedIngredients'] = df['Ingredients'].apply(parse_ingredients_list)
        
        # Further cleaning steps (if any) can be added here
        
        return df

