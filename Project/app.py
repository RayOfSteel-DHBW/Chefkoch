import streamlit as st
import os
from utils.data_processor import load_recipes
from utils.recipe_parser import parse_recipes
from models.ingredient_analyzer import IngredientAnalyzer

def streamlit_setup():
    st.title("Chefkoch Analyzer")
    st.sidebar.header("Data Source")
    
def load_data():
    dataLoader = DataLoader()
    dataLoader.LoadData()
    return dataLoader.data

def visualize():
    #


def main():
    streamlit_setup()
    
    dataFrame = load_data()
    
    file_path = os.path.join("..", "DemoData.json")
    
    if os.path.exists(file_path):
        data = load_recipes(file_path)
        recipes = parse_recipes(data)
    
    # else:
    #     st.error(f"Error: Could not find {file_path}")

if __name__ == "__main__":
    main()