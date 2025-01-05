import csv
from typing import List, Optional, Union
from .ffxivitem import FFXIVItem
from .xivapi import XIVAPI
from .recipe import Recipe
from .recipes import Recipes
import os

class CSVDB:
    def __init__(self):
        self.items_file = os.path.join('csv', 'items.csv')
        self.worlds_file = os.path.join('csv', 'worlds.csv')
        self._ensure_files_exist()
        self.items = self.load_items()
        self.worlds = self.load_worlds()
        self.xivapi = XIVAPI()
        self.recipes = Recipes()

    def _ensure_files_exist(self) -> None:
        """
        Ensure that the items.csv and worlds.csv files exist. If not, create them.
        """

        if not os.path.exists(self.items_file):
            with open(self.items_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['item_name', 'item_id', 'emoji', 'category', 'icon_url'])
                writer.writeheader()


        if not os.path.exists(self.worlds_file):
            with open(self.worlds_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['world_name'])

    def load_items(self) -> dict:
        """
        Load items from the items.csv file.

        Returns:
        - dict: A dictionary of FFXIVItem instances with item_id as the key.
        """
        items = {}
        with open(self.items_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                item = FFXIVItem(
                    item_name=row.get('item_name', 'Unknown'),
                    item_id=int(row.get('item_id', 0)),
                    emoji=row.get('emoji', ''),
                    category=row.get('category', ''),
                    icon_url=row.get('icon_url', '')
                )
                items[item.item_id] = item
        return items

    def search_world_by_id(self, world_id: int) -> Optional[str]:
        """
        Search for a world by its ID.

        Parameters:
        - world_id (int): The ID of the world to search for.

        Returns:
        - Optional[str]: The found world name or None if not found.
        """
        if world_id in self.worlds:
            return self.worlds[world_id]
        return None

    def load_worlds(self) -> dict:
        """
        Load worlds from the worlds.csv file.

        Returns:
        - dict: A dictionary of world names with world_id as the key.
        """
        worlds = {}
        with open(self.worlds_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                world_id = int(row.get('id', 0))
                world_name = row.get('name', 'Unknown')
                worlds[world_id] = world_name
        return worlds


    def fuzzy_search_item(self, name: str) -> Optional[list]:
        """
        Perform a fuzzy search for an item by its name using the local CSVDB.
        Return a list of FFXIVItem instances in order of closeness.
        """
        from difflib import get_close_matches

        # Get all item names from the local database
        item_names = [item.item_name for item in self.items.values()]

        # Find close matches to the provided name
        close_matches = get_close_matches(name, item_names, n=5, cutoff=0.6)

        # Sort the items based on the order of closeness
        matching_items = sorted(
            (item for item in self.items.values() if item.item_name in close_matches),
            key=lambda item: close_matches.index(item.item_name)
        )

        # Return the list of matching FFXIVItem instances
        return matching_items if matching_items else None



    def update(self, updated_item: FFXIVItem) -> None:
        """
        Update an FFXIVItem in the items.csv file. If the item does not exist, add it.

        Parameters:
        - updated_item (FFXIVItem): The item to update or add.
        """
        if updated_item.item_id in self.items:
            # Override all data where existing from the updated_item
            existing_item = self.items[updated_item.item_id]
            if (existing_item.item_name != updated_item.item_name or
                existing_item.emoji != updated_item.emoji or
                existing_item.category != updated_item.category or
                existing_item.icon_url != updated_item.icon_url):
                
                existing_item.item_name = updated_item.item_name
                existing_item.emoji = updated_item.emoji
                existing_item.category = updated_item.category
                existing_item.icon_url = updated_item.icon_url
                self.sync_csv()
       
        else:
            # Add the new item to the internal item database
            self.items[updated_item.item_id] = updated_item
            self.append_item_to_csv(updated_item)

        # Call the function to update the CSV file
        



    def search_item_by_id(self, item_id: int) -> Optional[FFXIVItem]:
        """
        Search for an item by its ID.

        Parameters:
        - item_id (int): The ID of the item to search for.

        Returns:
        - Optional[FFXIVItem]: The found item or None if not found.
        """
        if item_id in self.items:
            return self.items[item_id]
        # If item is not found in the database, attempt to fetch from XIVAPI
        return self.fetch_item_info_from_xivapi(item_id)

    def search_item_by_name(self, item_name: str) -> Optional[FFXIVItem]:
        """
        Search for an item by its name.

        Parameters:
        - item_name (str): The name of the item to search for.

        Returns:
        - Optional[FFXIVItem]: The found item or None if not found.
        """
        for item in self.items.values():
            if item.item_name.lower() == item_name.lower():
                print(f"[CSVDB][search_item_by_name] Item {item_name} found in the database.")
                return item
        return self.fetch_item_info_from_xivapi(item_name)

    def sync_csv(self) -> None:
        """
        Update an item in the items.csv file.

        Parameters:
        - item (FFXIVItem): The item to update.
        """
        with open(self.items_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['item_name', 'item_id', 'emoji', 'category', 'icon_url'])
            writer.writeheader()
            for item in self.items.values():
                writer.writerow({
                    'item_name': item.item_name,
                    'item_id': item.item_id,
                    'emoji': item.emoji,
                    'category': item.category,
                    'icon_url': item.icon_url
                })

    def append_item_to_csv(self, ffxivitem: FFXIVItem) -> None:
        """
        Append a new FFXIVItem instance to the items.csv file if it is not already in the items array.

        Parameters:
        - ffxivitem (FFXIVItem): The FFXIVItem instance to write.
        """
        with open(self.items_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['item_name', 'item_id', 'emoji', 'category', 'icon_url'])
           
            writer.writerow({
                'item_name': ffxivitem.item_name,
                'item_id': ffxivitem.item_id,
                'emoji': ffxivitem.emoji,
                'category': ffxivitem.category,
                'icon_url': ffxivitem.icon_url
            })


    def fetch_item_info_from_xivapi(self, identifier: Union[int, str]) -> Optional[FFXIVItem]:
        """
        Fetch item information from XIVAPI using the provided item ID or name.
        If the item is not in the database, add it and update the CSV file.

        Parameters:
        - identifier (Union[int, str]): The ID or name of the item to fetch.

        Returns:
        - Optional[FFXIVItem]: The fetched item or None if an error occurs.
        """

        if isinstance(identifier, int):
            data = self.xivapi.get_item_info(identifier)
        else:
            data = self.xivapi.item_search(identifier)

        if data and "results" in data and data["results"]:
            data = data["results"][0]
        else:
            return None

        # Create a new FFXIVItem instance and auto-fill its information
        new_item = FFXIVItem("", 0, "", "", "")
        if new_item.auto_fill_info_from_xivapi(data):
            # Add the new item to the database and update the CSV file only if data was successfully filled
            self.update(new_item)
            return new_item
        else:
            return None
        


    def search_recipes(self, identifier: Union[int, str]) -> Optional[Recipe]:
        """
        Auto detects if the identifier is a digit (item ID) or a name and calls the correct search recipe command.

        Parameters:
        - identifier (Union[int, str]): The item ID or name to search for.

        Returns:
        - Optional[Recipe]: The recipe details or None if not found.
        """
        if isinstance(identifier, int) or identifier.isdigit():
            return self.search_recipes_by_item_id(int(identifier))
        else:
            return self.search_recipes_by_item_name(identifier)


    def search_recipes_by_item_id(self, item_id: int) -> Optional[Recipe]:
        """
        Search for a recipe by its item ID.

        Parameters:
        - item_id (int): The item ID to search for.

        Returns:
        - Optional[Recipe]: The recipe details or None if not found.
        """
        return self.recipes.search_recipes_by_item_id(item_id)

    def search_recipes_by_item_name(self, item_name: str) -> Optional[Recipe]:
        """
        Search for a recipe by its item name.

        Parameters:
        - item_name (str): The item name to search for.

        Returns:
        - Optional[Recipe]: The recipe details or None if not found.
        """
        item = self.search_item_by_name(item_name)
        if item:
            return self.search_recipes_by_item_id(item.item_id)
        else:
            return None
