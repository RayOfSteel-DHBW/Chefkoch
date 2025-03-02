import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_top_category_ratings(dataset):
    """
    Create line plots for rating distribution of the 5 largest categories.
    """
    # Set plot style
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Find the 5 largest categories
    category_counts = dataset['category'].value_counts()
    top_5_categories = category_counts.index[:5]
    
    # Create line plots for each category's rating distribution
    for category in top_5_categories:
        category_ratings = dataset[dataset['category'] == category]['rating']
        sns.kdeplot(category_ratings, label=category)
    
    # Add labels and title
    plt.xlabel("Rating")
    plt.ylabel("Density")
    plt.title("Rating Distribution for Top 5 Categories")
    plt.legend()
    
    # Display the plot
    plt.tight_layout()
    plt.show()