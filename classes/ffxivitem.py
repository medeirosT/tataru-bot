from typing import Optional
from .recipe import Recipe
class FFXIVItem:

    # Constructor for the FFXIVItem class   
    def __init__(self, item_name: str, item_id: int, emoji: str, category: str, icon_url: str):
        self._item_name = item_name
        self._item_id = item_id
        self._emoji = emoji
        self._category = category
        self._icon_url = icon_url
        self._recipes = []

    # Getter and Setter for item_name
    @property
    def item_name(self) -> str:
        return self._item_name

    @item_name.setter
    def item_name(self, value: str) -> None:
        self._item_name = value

    # Getter and Setter for item_id
    @property
    def item_id(self) -> int:
        return self._item_id

    @item_id.setter
    def item_id(self, value: int) -> None:
        self._item_id = value

    # Getter and Setter for emoji
    @property
    def emoji(self) -> str:
        return self._emoji
    
    def auto_fill_info_from_xivapi(self, result: dict) -> Optional['FFXIVItem']:
        """
        Auto fills the item information based on the provided result object.

        Parameters:
        - result (dict): The result object containing item information.

        Returns:
        - Optional[FFXIVItem]: Returns self if successful, None if an exception occurred.
        """
        try:
            if "ID" in result:
                print("Handling STABLE xivapi result")
                # Handling STABLE xivapi result
                self._item_id = result["ID"]
                self._item_name = result["Name"]
                self._category = result["ItemUICategory"]["Name"]
                self._emoji = self.get_emoji_name_from_item(self._category)
                self._icon_url = f"https://xivapi.com{result["Icon"]}"
                if "recipes" in result and result["recipes"]:
                    for recipe_data in result["recipes"]:
                        recipe = Recipe(
                            classId=recipe_data["ClassJobID"],
                            recipe_id=recipe_data["ID"],
                            recipe_level=recipe_data["RecipeLevel"]
                        )
                        # Assuming no ingredients are provided in the new structure
                        self._recipes.append(recipe)
                print("[FFXIVItem][auto_fill_info_from_xivapi] Handled STABLE xivapi result")
            else:   
                print("[FFXIVItem][auto_fill_info_from_xivapi] Handling BETA xivapi result")
                # Handling BETA xivapi result   
                fields = result["fields"]
                self._item_id = result["row_id"]
                self._item_name = fields["Name"]
                self._category = fields["ItemSearchCategory"]["fields"]["Name"]
                self._emoji = self.get_emoji_name_from_item(self._category)
                icon_path = fields.get('Icon', {}).get('path', '')
                self._icon_url = f"https://beta.xivapi.com/api/1/asset/{icon_path}?format=png"

                print("[FFXIVItem][auto_fill_info_from_xivapi] Handled BETA xivapi result")

            return self
        except KeyError as e:
            print(f"[FFXIVItem][auto_fill_info_from_xivapi] Error auto-filling item info: {e}")
            return None


    @emoji.setter
    def emoji(self, value: str) -> None:
        self._emoji = value

    # Getter and Setter for category
    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        self._category = value

    # Getter and Setter for icon_url
    @property
    def icon_url(self) -> str:
        return self._icon_url

    @icon_url.setter
    def icon_url(self, value: str) -> None:
        self._icon_url = value


    @staticmethod
    def get_emoji_name_from_item(category_name: str) -> str:
        """
        Takes a category name as a string and returns an emoji name depending on the value of the ItemSearchCategory.

        Parameters:
        - category_name (str): The name of the item category.

        Returns:
        - str: The emoji name corresponding to the ItemSearchCategory.
        """

        category_name = category_name.lower()

        if category_name == "minions":
            return "🐾"
        elif category_name == "wall-mounted" or category_name == "paintings":
            return "🖼️"
        elif category_name == "body":
            return "👕"
        elif category_name == "interior fixtures" or category_name == "outdoor furnishings" or category_name == "exterior fixtures":
            return "🏠"
        elif category_name == "materia":
            return "🔴"
        elif category_name == "crafting material":
            return "🛠️"
        elif category_name == "rings":
            return "💍"
        elif category_name == "consumable":
            return "🍴"
        elif category_name == "furnishings" or category_name == "tabletop" or category_name == "rugs" or category_name == "tables":
            return "🛋️"
        elif category_name == "weapon" or category_name == "weapon parts":
            return "⚔️"
        elif category_name == "armor" or category_name == "armor parts" or category_name == "shields":
            return "🛡️"
        elif category_name == "tools" or "'s tools" in category_name:
            return "🔧"
        elif category_name == "seafood":
            return "🍣"
        elif category_name == "fish":
            return "🐟"
        elif category_name == "ingredients":
            return "🥕"
        elif category_name == "gardening items":
            return "🌱"
        elif category_name == "dyes":
            return "🎨"
        elif category_name == "mount":
            return "🐴"
        elif category_name == "orchestrion roll":
            return "🎵"
        elif category_name == "mineral":
            return "⛏️"
        elif category_name.startswith("reagent") or category_name == "medicine":
            return "⚗️"
        elif category_name == "stone" or category_name.startswith("catalyst"):
            return "🪨"
        elif category_name == "metal":
            return "🧱"
        elif category_name == "chairs and beds":
            return "🛏️"
        elif category_name == "leather":
            return "💼"
        elif category_name == "tables":
            return "🪑"
        elif category_name == "meals":
            return "🍱"
        elif category_name == "cloth" or category_name == "cloths":
            return "🧵"
        elif category_name == "heads" or category_name == "head":
            return "👒"
        elif category_name == "hands" or category_name == "hand":
            return "👐"
        elif category_name == "legs":
            return "👖"
        elif category_name == "bone" or category_name == "bones":
            return "🦴"
        elif category_name == "feet":
            return "👠"
        elif category_name == "bracelets" or category_name == "bracelet" or category_name == "earrings" or category_name == "earring":
            return "💍"
        elif category_name == "necklaces":
            return "📿"
        elif category_name == "lumber":
            return "🪵"
        elif category_name == "registrable miscellany":
            return "🃏"
        elif "'s arms" in category_name:
            return "⚔️"
        elif category_name.startswith("crystal"):
            return "🔮"
        elif category_name == "fishing tackle":
            return "🎣"
        elif category_name == "orchestrion components":
            return "🎵"
        elif category_name == "miscellany" or category_name == "miscellany":
            return "🛒"
        elif category_name == "miscellaneous":
            return "❓"
        else:
            print("Could not find emoji for item type: ", category_name)
            return "❓"