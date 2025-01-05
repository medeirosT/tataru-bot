import csv
import os
import requests
from typing import Optional, List
from .recipe import Recipe

class Recipes:
    def __init__(self):
        self.recipes_file = os.path.join('csv', 'recipes.csv')
        self._ensure_file_exists()
        self.recipes = self.load_recipes()

    def _ensure_file_exists(self) -> None:
        """
        Ensure that the recipes.csv file exists. If not, download it.
        """
        if not os.path.exists(self.recipes_file):
            url = "https://raw.githubusercontent.com/xivapi/ffxiv-datamining/refs/heads/master/csv/Recipe.csv"
            response = requests.get(url)
            response.raise_for_status()
            with open(self.recipes_file, mode='wb') as file:
                file.write(response.content)
            print(f"[Recipes][_ensure_file_exists] {self.recipes_file} did not exist and was downloaded.")
        else:
            print(f"[Recipes][_ensure_file_exists] {self.recipes_file} exists.")

    def load_recipes(self) -> dict:
        """
        Load recipes from the recipes.csv file.

        Returns:
        - dict: A dictionary of Recipe objects with recipe_number as the key.
        """
        print(f"[Recipes][load_recipes] Loading recipes from {self.recipes_file}")
        recipes = {}
        with open(self.recipes_file, mode='r', newline='', encoding='utf-8') as file:
            # End Generation Here
            # Skip the first three lines of the header
            for _ in range(3):
                next(file)
            reader = csv.reader(file)
            for row in reader:
    
                recipe_number = int(row[0])
                item_id = int(row[5])
                if item_id == 0:
                    continue
                amount = int(row[6])
                craftType = int(row[2])
                recipe = Recipe(craftType=craftType, recipe_number=recipe_number, itemID=item_id, amount=amount)  # Assuming classId and recipe_level are not in CSV
          
                for i, index in enumerate(range(7, 22, 2)):
                    ingredient_id = int(row[index])
                    ingredient_amount = int(row[index + 1])
                    if ingredient_id > 0:  # Assuming 0 or negative means no ingredient
                        recipe.set_ingredient(itemID=ingredient_id, amount=ingredient_amount, index=i)

                recipes[recipe_number] = recipe
        print(f"[Recipes][load_recipes] Loaded {len(recipes)} recipes from {self.recipes_file}.")
        return recipes

    def search_recipe_by_number(self, recipe_number: int) -> Optional[dict]:
        """
        Search for a recipe by its recipe number.

        Parameters:
        - recipe_number (int): The recipe number to search for.

        Returns:
        - Optional[dict]: The recipe details or None if not found.
        """
        return self.recipes.get(recipe_number)

    def search_recipes_by_item_id(self, item_id: int) -> List[Recipe]:
        """
        Search for recipes by their item ID.

        Parameters:
        - item_id (int): The item ID to search for.

        Returns:
        - List[Recipe]: A list of recipes that match the item ID or an empty list if none are found.
        """
        matching_recipes = []
        for recipe in self.recipes.values():
            if recipe.itemID == item_id:
                matching_recipes.append(recipe)
        return matching_recipes
