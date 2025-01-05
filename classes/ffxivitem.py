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

        emoji_map = {
            "minions": "🐾",
            "wall-mounted": "🖼️",
            "paintings": "🖼️",
            "body": "👕",
            "interior fixtures": "🏠",
            "outdoor furnishings": "🏠",
            "exterior fixtures": "🏠",
            "materia": "🔴",
            "crafting material": "🛠️",
            "rings": "💍",
            "consumable": "🍴",
            "furnishings": "🛋️",
            "tabletop": "🛋️",
            "rugs": "🛋️",
            "tables": "🛋️",
            "weapon": "⚔️",
            "weapon parts": "⚔️",
            "armor": "🛡️",
            "armor parts": "🛡️",
            "shields": "🛡️",
            "seafood": "🍣",
            "fish": "🐟",
            "gardening items": "🌱",
            "dyes": "🎨",
            "mount": "🐴",
            "orchestrion roll": "🎵",
            "mineral": "⛏️",
            "stone": "🪨",
            "metal": "🧱",
            "chairs and beds": "🛏️",
            "leather": "💼",
            "meals": "🍱",
            "cloth": "🧵",
            "cloths": "🧵",
            "heads": "👒",
            "head": "👒",
            "hands": "👐",
            "hand": "👐",
            "legs": "👖",
            "bone": "🦴",
            "bones": "🦴",
            "feet": "👠",
            "bracelets": "💍",
            "bracelet": "💍",
            "earrings": "💍",
            "earring": "💍",
            "necklaces": "📿",
            "lumber": "🪵",
            "registrable miscellany": "🃏",
            "fishing tackle": "🎣",
            "orchestrion components": "🎵",
            "miscellany": "🛒",
            "miscellaneous": "❓"
        }

        # Check for specific conditions
        if "'s tools" in category_name:
            return "🔧"
        elif "'s arms" in category_name:
            return "⚔️"
        elif category_name.startswith("ingredients"):
            return "🥕"
        elif category_name.startswith("reagent") or category_name == "medicine":
            return "⚗️"
        elif category_name.startswith("catalyst"):
            return "🪨"
        elif category_name.startswith("crystal"):
            return "🔮"

        # Return emoji from map or default
        return emoji_map.get(category_name, "❓")
