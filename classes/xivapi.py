import requests
from typing import Optional
import urllib.parse


class XIVAPI:
    SEARCH_URL = "https://beta.xivapi.com/api/1/search?sheets=Item&query=%2BName~%22{serialized_name}%22+%2BItemSearchCategory%3E%3D1&language=en&limit=30&fields=Name,ItemSearchCategory,Icon"
    ITEM_INFO_URL = "https://xivapi.com/item/{identifier}"
    

    def item_search(self, name: str) -> Optional[dict]:
        """
        Search for an item by its name using XIVAPI.

        Parameters:
        - name (str): The name of the item to search for.

        Returns:
        - Optional[dict]: The search results or None if an error occurs.
        """
        print(f"[XIVAPI][item_search] Searching for item: {name}")
        try:
    
            
            serialized_name = urllib.parse.quote(name)
            url = self.SEARCH_URL.format(serialized_name=serialized_name)
            response = requests.get(url)
            response.raise_for_status()
            print(f"[XIVAPI][item_search] Response: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"[item_search] Error fetching item from XIVAPI: {e}")
            return None

    def get_item_info(self, identifier: int) -> Optional[dict]:
        """
        Get item information by its ID using XIVAPI.

        Parameters:
        - identifier (int): The ID of the item to fetch.

        Returns:
        - Optional[dict]: The item information or None if an error occurs.
        """
        print(f"[XIVAPI][get_item_info] Fetching item info for ID: {identifier}")
        try:
            url = self.ITEM_INFO_URL.format(identifier=identifier)
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[get_item_info] Error fetching item from XIVAPI: {e}")
            return None

