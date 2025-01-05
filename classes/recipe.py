from typing import Optional

class Recipe:
    def __init__(self, craftType: int, recipe_number: int, itemID: int, amount: int  ):
        self.craftType = craftType
        self.recipe_number = recipe_number
        self.itemID = itemID
        self.amount = amount
        self.ingredients = [None] * 8

    def set_ingredient(self, itemID: int, amount: int, index: int) -> None:
        """
        Set an ingredient in the recipe by index.

        Parameters:
        - ffxivitem (FFXIVItem): The FFXIVItem instance to set.
        - classId (int): The class ID associated with the ingredient.
        - amount (int): The amount of the ingredient.
        - index (int): The index at which to set the ingredient (0-7).
        """
        if 0 <= index < 8:
            self.ingredients[index] = {'itemID': itemID, 'amount': amount}
        else:
            raise IndexError("Recipe.set_ingredient: Index out of range. Must be between 0 and 7.")


    def get_ingredient_by_index(self, index: int) -> Optional[dict]:
        """
        Get an ingredient from the recipe by index.

        Parameters:
        - index (int): The index of the ingredient to retrieve (0-7).

        Returns:
        - Optional[dict]: A dictionary containing the ingredient details or None if the index is out of range.
        """
        if 0 <= index < 8:
            return self.ingredients[index]
        else:
            raise IndexError("Recipe.get_ingredient_by_index: Index out of range. Must be between 0 and 7.")


    def get_craftTypeName(self) -> str:
        """
        Get the name of the craft type based on the craftType ID.

        Returns:
        - str: The name of the craft type.
        """
        craftTypeNames = {
            0: "🪚Woodworking",
            1: "🔨Smithing",
            2: "🛡️Armorcraft",
            3: "💍Goldsmithing",
            4: "👜Leatherworking",
            5: "🧶Clothcraft",
            6: "🧪Alchemy",
            7: "🍳Cooking"
        }
        return craftTypeNames.get(self.craftType, "Unknown")

    def get_recipe_number(self) -> int:
        """
        Get the raw ID of the recipe.

        Returns:
        - int: The raw ID of the recipe.
        """
        return self.recipe_number
