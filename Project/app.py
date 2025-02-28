import streamlit as st
import os
from Project import data_loader
from models.ingredient_analyzer import IngredientAnalyzer

def streamlit_setup():
    st.title("Chefkoch Analyzer")
    st.sidebar.header("Data Source")
    
def load_data():
    dataLoader = data_loader()
    return dataLoader.load_data_and_clean()


def visualize():
    //

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