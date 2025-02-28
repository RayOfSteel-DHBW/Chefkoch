from typing import Tuple
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import re

class data_handler:
        
    def load(self) -> pd.DataFrame:
        return dataFrame

    def fix_ingredient_column(self, dataFrame) -> pd.DataFrame:
        if 'ingredients' in dataFrame.columns:
            processed_ingredients = []
            for idx, row in dataFrame.iterrows():
                if isinstance(row['ingredients'], str):
                    ingredient_list = row['ingredients'].split('+')
                    clean_ingredients = []
                    
                    for ingredient_str in ingredient_list:
                        clean_ing = re.sub(r'<U\+[0-9A-F]{4}>', '', ingredient_str).strip()
                        if clean_ing:
                            clean_ingredients.append(clean_ing)
                    
                    processed_ingredients.append(clean_ingredients)
                else:
                    processed_ingredients.append([])
            
            dataFrame['cleaned_ingredients'] = processed_ingredients
        
        return dataFrame

    def Preprocess(self, dataFrame) -> pd.DataFrame:
        if dataFrame is not None:
            dataFrame = dataFrame.dropna()
            dataFrame = self.fix_ingredient_column(dataFrame)
            return dataFrame
            
        return dataFrame
