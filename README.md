# Tataru Bot

Tataru bot is a tool I made in my free time to help me with my FFXIV crafting, help my friends and Free Company, and also to learn more about Python and Discord API.
It gives you the price of an item, the recipe to craft it, and the ingredients you need to craft it. (As well as self-reliance mode for recipes)

Code isn't perfect, but it's functional and I'm proud of it.


## Features

- Search for items by name or ID using XIVAPI.
- Fetch detailed item information from XIVAPI.
- Manage a local CSV database of items.
- Perform fuzzy searches for items.
- Search for recipes by item name or ID.
- Integrate with Discord to provide item information in real-time.

## Setup

### Prerequisites

- Python 3.6 or higher
- `requests` library
- `discord.py` library

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/medeirosT/tataru-bot.git
    cd tataru-bot
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
    or if you're on Debian/Ubuntu:
    ```sh
    pip3 install -r requirements.txt
    ```

3. Edit main.py and add your discord bot token and channel id, as well as the role id you want to give to the users that use the bot.

4. Run the bot:
    ```sh
    python3 bot.py
    ```

## Usage

### Example Commands on Discord

1. **Search for an item by name:**
    ```
    !search Lesser Panda
    ```

2. **Fetch price information by ID:**
    ```
    !price 12056
    ```

3. **Search for a recipe by item name:**
    ```
    !recipe Lesser Panda
    ```

4. **Search for a recipe by item ID:**
    ```
    !recipe 12056
    ```
    
5. **Manually update an emoji for an item ID:**
    ```
    !setemoji 10335 🪨
    ```
    
## Why Tataru?

If you played FFXIV, you'll know her entrepreneurial spirit. That's what inspired the name.


## Screenshots
![image](https://github.com/user-attachments/assets/5093a6f6-1fde-4e90-b153-a9f8e612c5a5)
![image](https://github.com/user-attachments/assets/460e509a-47db-4f8e-afac-83f1584e59d2)
![image](https://github.com/user-attachments/assets/0cee5ca4-2cd3-46cb-b9af-c8c19e3a9814)

