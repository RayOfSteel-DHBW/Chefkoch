from pathlib import Path
import sys
import pandas as pd
import sqlite3
import category_ingredient_analyzer
import analyzer
import category_analyzer

def display_menu():
    print("\n=== Chefkoch Analysis Menu ===")
    print("1) Rating Distribution")
    print("2) Best Rated Category")
    print("3) Most Common Combination of Ingredients per Category")
    print("4) Top 3 Most Impactful Ingredient per Category")
    print("5) Most Common Tag Combinations")
    print("6) Category Archetypes")
    print("0) Exit")

def main():
    #somehow I didn't manage to use a relative path here ... idk why
    dbPath = r"C:\Users\raine\OneDrive\Dokumente\Uni\ScientificProgramming\Chefkoch\Data\crawled_data.db"
    
    if(not Path(dbPath).exists()):
        print("Database not found. Please run the Crawler first.")
        sys.exit(1)
    conn = sqlite3.connect(dbPath)
    while True:
        display_menu()
        choice = input("\nEnter your selection (0-6): ")
        if choice == "1":
            analyze_rating_distribution(conn)
        elif choice == "2":
            find_best_rated_category(conn)
        elif choice == "3":
            analyze_common_ingredient_combinations(conn)
        elif choice == "4":
            find_top_impactful_ingredients(conn)
        elif choice == "0":
            print("Exiting program...")
            sys.exit(0)
        else:
            print("Invalid option. Please select a number between 0 and 6.")
        
        input("\nPress Enter to continue...")

def analyze_rating_distribution(conn):
    print("\nAnalyzing rating distribution...")    
    query = """
    SELECT r.recipe_id, r.name, r.rating, c.name as category 
    FROM recipemodel r
    JOIN categorymodel c ON r.category_id = c.category_id
    WHERE r.rating IS NOT NULL"""
    
    dataFrame = pd.read_sql_query(query, conn)
    
    # Check if we have data before analysis
    if dataFrame.empty:
        print("No rating data available for analysis.")
        return
        
    # Make sure we have the expected columns
    if 'rating' not in dataFrame.columns or 'category' not in dataFrame.columns:
        print("Missing required columns for analysis.")
        return
        
    analyzer.analyze_rating_distribution(dataFrame)

def find_best_rated_category(conn):
    dataframe = pd.read_sql_query("SELECT c.category_id, c.name as category_name, r.recipe_id, r.rating from recipemodel r join categorymodel c on r.category_id = c.category_id", conn)
    category_analyzer.analyze_best_rated_categories(dataframe)
    print("\nFinding the best rated category...")

def analyze_common_ingredient_combinations(conn):
    print("\nAnalyzing most common combinations of ingredients per category...")
    # Query to get ingredients by recipe and category
    query = """
    SELECT c.name as category_name, r.recipe_id, i.name as ingredient_name
    FROM recipemodel r 
    JOIN categorymodel c ON r.category_id = c.category_id
    JOIN recipeingredientthroughmodel ri ON r.recipe_id = ri.recipe_id
    JOIN ingredientmodel i ON ri.ingredient_id = i.ingredient_id
    """
    dataframe = pd.read_sql_query(query, conn)
    category_ingredient_analyzer.analyze_common_ingredient_combinations(dataframe)

def find_top_impactful_ingredients(conn):
    print("\nFinding top impactful ingredients per category...")
    query = """
    SELECT 
        c.name as category_name, 
        r.recipe_id, 
        r.rating,
        i.ingredient_id,
        i.name as ingredient_name
    FROM recipemodel r 
    JOIN categorymodel c ON r.category_id = c.category_id
    JOIN recipeingredientthroughmodel ri ON r.recipe_id = ri.recipe_id
    JOIN ingredientmodel i ON ri.ingredient_id = i.ingredient_id
    WHERE r.rating IS NOT NULL
    """
    
    dataframe = pd.read_sql_query(query, conn)
    category_ingredient_analyzer.analyze_impactful_ingredients(dataframe)


if __name__ == "__main__":
    main()