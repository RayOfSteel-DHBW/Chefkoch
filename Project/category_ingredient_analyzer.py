import itertools
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from collections import defaultdict

def analyze_common_ingredient_combinations(dataframe, top_n=5, combination_size=2):
    """
    Analyzes the most common combinations of ingredients per category.
    
    Parameters:
    dataframe: DataFrame containing recipe_id, category_name, and ingredient_name
    top_n: Number of top combinations to show per category
    combination_size: Size of ingredient combinations (pairs, triplets, etc.)
    """
    # Check if dataframe has the required columns
    required_columns = ['recipe_id', 'category_name', 'ingredient_name']
    if not all(col in dataframe.columns for col in required_columns):
        print(f"Error: Dataframe must contain columns {required_columns}")
        return
    
    # Group by recipe and category to get ingredients per recipe
    recipe_ingredients = dataframe.groupby(['recipe_id', 'category_name'])['ingredient_name'].apply(list).reset_index()
    
    # Initialize a dictionary to store combinations by category
    category_combinations = {}
    
    # Process each category
    for category_name in dataframe['category_name'].unique():
        category_recipes = recipe_ingredients[recipe_ingredients['category_name'] == category_name]
        
        # Skip categories with too few recipes
        if len(category_recipes) < 5:
            continue
            
        # Generate all possible combinations for each recipe
        all_combinations = []
        for _, row in category_recipes.iterrows():
            ingredients = row['ingredient_name']
            # Only consider recipes with enough ingredients for the requested combination size
            if len(ingredients) >= combination_size:
                # Generate all combinations of the specified size
                combos = list(itertools.combinations(sorted(ingredients), combination_size))
                all_combinations.extend(combos)
        
        # Count combinations
        combination_counts = Counter(all_combinations)
        top_combinations = combination_counts.most_common(top_n)
        
        # Store in dictionary
        category_combinations[category_name] = top_combinations
    
    # Display the results
    print(f"\n=== Most Common {combination_size}-Ingredient Combinations by Category ===")
    
    for category, combinations in sorted(category_combinations.items()):
        if combinations:
            print(f"\nCategory: {category}")
            for i, (combo, count) in enumerate(combinations, 1):
                print(f"{i}. {' + '.join(combo)}: {count} recipes")
        else:
            print(f"\nCategory: {category} - Not enough data for analysis")
    
    # Visualize the top combinations for the top categories
    visualize_top_ingredient_combinations(category_combinations, combination_size)

def visualize_top_ingredient_combinations(category_combinations, combination_size):
    """
    Creates visualizations for the most common ingredient combinations.
    
    Parameters:
    category_combinations: Dictionary of categories and their top combinations
    combination_size: Size of the combinations being visualized
    """
    # Select top categories based on the count of their most common combination
    top_categories = sorted(
        [(cat, combs) for cat, combs in category_combinations.items() if combs],
        key=lambda x: x[1][0][1] if x[1] else 0,
        reverse=True
    )[:min(3, len(category_combinations))]
    
    if top_categories:
        # Create a figure with subplots for each top category
        fig, axes = plt.subplots(len(top_categories), 1, figsize=(12, 5*len(top_categories)))
        
        # If there's only one subplot, axes won't be iterable
        if len(top_categories) == 1:
            axes = [axes]
        
        # For each top category, create a bar plot
        for i, (category, combinations) in enumerate(top_categories):
            # Prepare data for plotting
            combo_labels = [' + '.join(combo[0]) for combo in combinations]
            combo_counts = [combo[1] for combo in combinations]
            
            # Create bar plot
            sns.barplot(x=combo_counts, y=combo_labels, ax=axes[i], palette='viridis')
            
            axes[i].set_title(f'Top Ingredient Combinations in {category}')
            axes[i].set_xlabel('Number of Recipes')
            axes[i].set_ylabel(f'{combination_size}-Ingredient Combinations')
        
        plt.tight_layout()
        plt.show()
    else:
        print("No categories with sufficient data for visualization.")

def analyze_impactful_ingredients(dataframe):
    """
    Analyzes which ingredients have the strongest positive correlation with recipe ratings
    for each category.
    
    Args:
        dataframe: DataFrame with category_name, recipe_id, rating, ingredient_id, and ingredient_name
    """
    # Filter to ensure we have enough data
    min_recipes = 5
    
    # Dictionary to store results
    category_correlations = {}
    
    # Get unique categories
    categories = dataframe['category_name'].unique()
    
    for category in categories:
        # Get data for this category
        category_data = dataframe[dataframe['category_name'] == category]
        
        # Skip categories with too few recipes
        unique_recipes = category_data['recipe_id'].nunique()
        if unique_recipes < min_recipes:
            continue
            
        # Get unique ingredients in this category
        ingredients = category_data['ingredient_name'].unique()
        
        # Calculate correlation for each ingredient
        ingredient_correlations = []
        
        for ingredient in ingredients:
            # Create binary feature: 1 if recipe contains ingredient, 0 otherwise
            recipes = category_data['recipe_id'].unique()
            
            # Create mapping of recipe_id to whether it contains the ingredient
            recipe_has_ingredient = defaultdict(int)
            for _, row in category_data[category_data['ingredient_name'] == ingredient].iterrows():
                recipe_has_ingredient[row['recipe_id']] = 1
                
            # Create arrays for correlation calculation
            recipe_ratings = []
            ingredient_presence = []
            
            for recipe_id in recipes:
                recipe_data = category_data[category_data['recipe_id'] == recipe_id]
                if not recipe_data.empty:
                    rating = recipe_data['rating'].iloc[0]
                    recipe_ratings.append(rating)
                    ingredient_presence.append(recipe_has_ingredient[recipe_id])
            
            # Calculate correlation if we have enough data
            if len(recipe_ratings) >= min_recipes and sum(ingredient_presence) > 1 and sum(ingredient_presence) < len(recipe_ratings):
                corr, p_value = pearsonr(ingredient_presence, recipe_ratings)
                ingredient_correlations.append((ingredient, corr, p_value, sum(ingredient_presence)))
                
        # Sort by absolute correlation (strongest impact first)
        ingredient_correlations.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Store for this category
        if ingredient_correlations:
            category_correlations[category] = ingredient_correlations
    
    # Display results
    print("\n=== Top Impactful Ingredients by Category ===")
    
    # For each category, show top ingredients
    for category, correlations in category_correlations.items():
        # Only show if we have results
        if correlations:
            print(f"\nCategory: {category}")
            print(f"{'Ingredient':<25} {'Correlation':>10} {'Impact':>10} {'Occurrence':>10}")
            print("-" * 60)
            
            # Show top 3 positive and top 3 negative correlations
            top_pos = [c for c in correlations if c[1] > 0][:3]
            top_neg = [c for c in correlations if c[1] < 0][:3]
            
            # Show positive correlations (ingredients that improve rating)
            if top_pos:
                print("Ingredients that IMPROVE ratings:")
                for ingredient, corr, p_value, count in top_pos:
                    impact = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
                    print(f"{ingredient:<25} {corr:>10.3f} {impact:>10} {count:>10}")
            
            # Show negative correlations (ingredients that worsen rating)
            if top_neg:
                print("\nIngredients that WORSEN ratings:")
                for ingredient, corr, p_value, count in top_neg:
                    impact = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
                    print(f"{ingredient:<25} {corr:>10.3f} {impact:>10} {count:>10}")
    
    # Create visualizations for top categories
    top_categories = list(category_correlations.keys())[:3]
    if top_categories:
        plt.figure(figsize=(12, 10))
        
        for i, category in enumerate(top_categories):
            correlations = category_correlations[category]
            
            # Get top 5 positive and top 5 negative correlations
            top_correlations = sorted(correlations, key=lambda x: x[1], reverse=True)[:5]
            bottom_correlations = sorted(correlations, key=lambda x: x[1])[:5]
            plot_data = top_correlations + bottom_correlations
            
            # Create dataframe for plotting
            plot_df = pd.DataFrame({
                'Ingredient': [item[0] for item in plot_data],
                'Correlation': [item[1] for item in plot_data]
            })
            
            # Sort for better visualization
            plot_df = plot_df.sort_values('Correlation')
            
            # Create subplot
            plt.subplot(len(top_categories), 1, i+1)
            bars = plt.barh(plot_df['Ingredient'], plot_df['Correlation'], color=plt.cm.RdYlGn(np.interp(plot_df['Correlation'], [-1, 1], [0, 1])))
            plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            plt.title(f"Top Impactful Ingredients: {category}")
            plt.xlabel('Correlation with Rating')
            plt.tight_layout()
        
        plt.show()