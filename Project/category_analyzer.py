import matplotlib.pyplot as plt
import seaborn as sns

def analyze_best_rated_categories(dataframe):
    """
    Analyzes the rating data of recipes by category to find the best rated
    categories.
    
    dataframe: DataFrame containing category_id, category_name, recipe_id, and rating columns
    """
    # Group by category and calculate mean rating
    category_ratings = dataframe.groupby('category_name')['rating'].agg(['mean', 'count']).reset_index()
    category_ratings.columns = ['Category', 'Average Rating', 'Number of Recipes']
    
    # Sort by average rating in descending order
    category_ratings = category_ratings.sort_values(by='Average Rating', ascending=False)
    
    # Filter categories with at least 5 recipes to ensure statistical significance
    significant_categories = category_ratings[category_ratings['Number of Recipes'] >= 5].copy()
    
    # Display results
    print("\n=== Best Rated Categories ===")
    if significant_categories.empty:
        print("No categories with sufficient data found.")
    else:
        print(significant_categories.head(10).to_string(index=False))
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        sns.set_style("whitegrid")
        
        # Plot top 10 categories
        top_categories = significant_categories.head(10)
        ax = sns.barplot(x='Average Rating', y='Category', data=top_categories, 
                        palette='viridis')
        
        # Add number of recipes as text on bars
        for i, row in enumerate(top_categories.itertuples()):
            ax.text(row._2 + 0.05, i, f"({row._3} recipes)", 
                    va='center', fontsize=9)
            
        plt.title('Top 10 Categories by Average Rating')
        plt.xlabel('Average Rating')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.show()
        
        # Additional insights
        category_fun_facts(dataframe)


def category_fun_facts(dataframe):
    """Provides additional insights about the categories"""
    # Calculate rating distribution by category
    top_categories = dataframe.groupby('category_name')['rating'].agg(['mean', 'count']).nlargest(5, 'mean')
    
    # For the top categories, show rating distribution
    for category in top_categories.index:
        category_data = dataframe[dataframe['category_name'] == category]
        
        print(f"\nRating distribution for '{category}':")
        print(category_data['rating'].value_counts().sort_index().to_string())