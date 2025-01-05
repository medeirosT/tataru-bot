"""
Discord Bot Setup Instructions:

1. Go to Discord Developer Portal (https://discord.com/developers/applications)
2. Click 'New Application' and give it a name
3. Go to the 'Bot' section and click 'Add Bot'
4. Copy the bot token (keep this secret!)
5. Go to OAuth2 -> URL Generator
6. Select 'bot' scope and required permissions (e.g. Send Messages)
7. Use generated URL to invite bot to your server
8. Replace TOKEN below with your bot token

Requirements:
- Python 3.8 or higher
- discord.py library (install with: pip install discord.py)
"""



# Custom imports inside the classes folder
from classes.ffxivitem import FFXIVItem
from classes.csvdb import CSVDB

# Discord imports
import discord
from discord.ext import commands
from discord import Embed

# Official imports
import requests
from datetime import datetime
from typing import Optional
from classes.recipe import Recipe


# Bot setup with Python 3 type hints
intents: discord.Intents = discord.Intents.default()
intents.voice_states = False
intents.message_content = True  # Need this for sending messages
bot: commands.Bot = commands.Bot(command_prefix='!', intents=intents)

# Channel ID where messages will be sent
ROLE_ID:        int = <ROLE ID HERE>  # Configureable role ID
SERVER_NAME:    str = "<SERVER NAME HERE>"
TOKEN:          str = "<TOKEN HERE>"

# Initialize CSVDB and Recipe
csvdb = CSVDB()

def get_market_data(item_ids: list, message: discord.Message) -> list:
    """
    Get market data for specified item IDs from Universalis API.
    Returns a list of market data results.
    """
    results = []
    
    # Base URL for the Universalis API
    base_url = f"https://universalis.app/api/v2/aggregated/{SERVER_NAME}/"

    print(f"[Main][get_market_data] Fetching market data for {item_ids} requested by {message.author}")

    try:
        # Convert list of IDs to comma-separated string
        items_string = ",".join(map(str, item_ids))
        
        # Build full URL with item IDs
        url = f"{base_url}{items_string}"
        
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse response JSON
        data = response.json()
        
        # Extract items data
        if "items" in data:
            results = data["items"]
        else:
            results = [data]  # Single item response
            
        print(f"[Main][get_market_data] Market data fetched for {item_ids} requested by {message.author}")
        return results

    except requests.RequestException as e:
        print(f"[Main][get_market_data] Error fetching market data: {e}")
        return []
    except ValueError as e:
        print(f"[Main][get_market_data] Error parsing response: {e}")
        return []
    except Exception as e:
        print(f"[Main][get_market_data] Unexpected error: {e}")
        return []



@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Event handler for when a message is sent in a Discord channel.

    This function listens for messages and processes commands based on the message content.
    It currently supports the following commands:
    - !price: Queries the market price of an item.
    - !setemoji: Sets an emoji for an item.

    Parameters:
    - message (discord.Message): The message object containing the command and its context.

    Returns:
    - None: The function does not return a value but may send messages back to the Discord channel.
    """
    # Don't respond to our own messages
    if message.author == bot.user:
        return

    # Check if the message starts with the !price command
    if message.content.lower().startswith('!price'):
        await handle_price_command(message)
    # Check if the message starts with the !setemoji command
    elif message.content.lower().startswith('!setemoji'):
        await handle_setemoji_command(message)
    # Check if the message starts with the !search command
    elif message.content.lower().startswith('!search'):
        await handle_search_command(message)
    # Check if the message starts with the !recipe command
    elif message.content.lower().startswith('!recipe'):
        await handle_recipe_command(message)






async def create_recipe_embed(item: FFXIVItem, all_ingredients=False, craftType=None, recipe_amount=1, hide_reactions=False) -> discord.Embed:
    """
    Create an embed that contains all recipe ingredients and a note about the money react.

    Parameters:
    - recipe_name: The name of the recipe.
    - recipe_id: The ID of the recipe.
    - item: The FFXIVItem object containing item details.
    - all_ingredients: A list of tuples containing the amount and item object, pre-calculated from get_recipe_ingredients.
    - craftType: The type of craft associated with the recipe.

    Returns:
    - discord.Embed: The embed object containing the formatted ingredients list and note.
    """

    embed = Embed(title=f"Recipe for {recipe_amount}x {item.emoji}{item.item_name} (ID: {item.item_id})", color=0x00ff00)
    embed.set_thumbnail(url=item.icon_url)
    embed.add_field(name="Wiki", value=f"[Link](https://ffxiv.gamerescape.com/wiki/{item.item_name.replace(' ', '_')})", inline=True)
    embed.add_field(name="Universalis", value=f"[Link](https://universalis.app/market/{item.item_id})", inline=True)
    embed.add_field(name="Garland Tools", value=f"[Link](https://www.garlandtools.org/db/#item/{item.item_id})", inline=True)
    embed.add_field(name="Craft Type", value=craftType if craftType else item.category, inline=True)

    # Format the ingredients list
    full_ingredients_list = ""
    if all_ingredients:
        # Separate crystal ingredients from others
        crystal_ingredients = ""
        non_crystal_ingredients = ""

        for ingredient_id, amount in all_ingredients.items():
            ingredient_item = csvdb.search_item_by_id(ingredient_id)
            ingredient =  (
                f"{amount}x {ingredient_item.emoji}{ingredient_item.item_name} "
                f"(ID: {ingredient_item.item_id})\n"
            )   
            if ingredient_item.category.lower() == "crystal":
                crystal_ingredients += ingredient
            else:
                non_crystal_ingredients += ingredient

        full_ingredients_list = non_crystal_ingredients + crystal_ingredients

            
    embed.add_field(name="Ingredients", value=full_ingredients_list if full_ingredients_list else "No ingredients found", inline=False)
    if not hide_reactions:
        embed.add_field(name="Note", value="React with 💰 to get the price of the item. React with 📓 to see the full recipe.", inline=False)

    return embed






# Special note... if you need to fix this function, may god help you.
def get_recipe_ingredients(recipe: Recipe, recursive=False, multiplier=1):
    """
    Get all ingredients required for a recipe, optionally including sub-recipe ingredients.
    When recursive is True, breaks down craftable ingredients into their base materials.
    When recursive is False, simply lists the direct ingredients needed.

    Parameters:
    - recipe (Recipe): The recipe to get ingredients for
    - recursive (bool): Whether to break down craftable ingredients into their components
    - multiplier (int): Amount multiplier for ingredients (how many times to craft the recipe)

    Returns:
    - dict: Dictionary mapping ingredient IDs to required amounts
    """
    ingredients = {}
    
    # Loop through all ingredients in the recipe
    for i in range(8):  # Recipe has 8 possible ingredient slots
        ingredient = recipe.get_ingredient_by_index(i)
        if ingredient and ingredient['itemID'] > 0:  # Valid ingredient
            ingredient_id = ingredient['itemID']
            amount_needed = ingredient['amount'] * multiplier
            
            if recursive:
                # Check if this ingredient can be crafted
                sub_recipes = csvdb.search_recipes(ingredient_id)
                
                if sub_recipes:
                    # This ingredient can be crafted
                    sub_recipe = sub_recipes[0]  # Get first matching recipe
                    items_per_craft = sub_recipe.amount
                    
                    # Calculate how many times we need to craft this sub-recipe
                    crafts_needed = (amount_needed + items_per_craft - 1) // items_per_craft
                    
                    # Recursively get ingredients for sub-recipe
                    sub_ingredients = get_recipe_ingredients(sub_recipe, recursive=True, multiplier=crafts_needed)
                    
                    # Merge sub-ingredients into our ingredients
                    for sub_id, sub_amount in sub_ingredients.items():
                        ingredients[sub_id] = ingredients.get(sub_id, 0) + sub_amount
                else:
                    # This is a base ingredient (not craftable)
                    ingredients[ingredient_id] = ingredients.get(ingredient_id, 0) + amount_needed
            else:
                # Just add the direct ingredient without recursion
                ingredients[ingredient_id] = ingredients.get(ingredient_id, 0) + amount_needed

    return ingredients



async def handle_recipe_command(message: discord.Message, recipe_id: int = -1, full_recipe: bool = False) -> None:
    """
    Handles the '!recipe' command from a Discord message. This command allows users to get the basic recipe
    information for an item by its name or ID.

    Parameters:
    - message (discord.Message): The message object containing the command and its context.
    - recipe_id (int, optional): The ID of the recipe to handle, if provided.
    - full_recipe (bool): Whether to include sub-recipes' ingredients.

    Returns:
    - None: Sends a message back to the Discord channel with the basic recipe information or an error message.
    """
    
    # Determine the item identifier
    if recipe_id == -1:
        # Extract the item identifier (everything after !recipe)
        item_identifier = message.content[7:].strip()
        if not item_identifier:
            await message.channel.send("Please provide an item name or ID to get the recipe for. Example: `!recipe Dark Matter`")
            return
    else:
        item_identifier = recipe_id

    # Use search_recipes to find the recipes
    recipes = csvdb.search_recipes(item_identifier)

    if recipes:
        # Only process the first recipe
        recipe = recipes[0]
        
        # Fetch a temporary copy of the item details using the recipe's item ID from CSVDB
        item = csvdb.search_item_by_id(recipe.itemID)
        
        if item:


            if full_recipe:
                # React to the user's message to indicate success
                await message.add_reaction("📖")

            # Use get_recipe_ingredients to get all ingredients needed for the recipe
            all_ingredients = get_recipe_ingredients(recipe, recursive=full_recipe)

            # Create an embed message using create_recipe_embed
            embed = create_recipe_embed(item, all_ingredients, recipe.get_craftTypeName(), recipe.amount, hide_reactions=full_recipe)
         
        else:
            await message.channel.send(f"Failed to fetch item details for {item_identifier}")
            return
        
        # Send the embed message with additional text asking if the user wants to know the market price
        
        sent_message = await message.channel.send(embed=await embed)
        
        # React with a coin emoji
        
        if not full_recipe:
            await sent_message.add_reaction("💰")
            await sent_message.add_reaction("📓")

    else:
        await message.channel.send(f"No recipe found for {item_identifier}")




async def handle_search_command(message: discord.Message) -> None:
    """
    Handles the '!search' command from a Discord message. This command allows users to search for items
    by name and returns a list of matching items with their IDs and corresponding emojis if available.

    Parameters:
    - message (discord.Message): The message object containing the command and its context.

    Returns:
    - None: Sends a message back to the Discord channel with the search results or an error message.
    """


    # Extract the search query (everything after !search)
    query = message.content[8:].strip()
 
    if not query:
        await message.channel.send("Please provide an item name to search for. Example: `!search Dark Matter`")
        return

    try:
        # Use the xivapi to search for items by name
        search_results = csvdb.xivapi.item_search(query)
        len_results = len(search_results['results'])
        if not search_results['results']:
            # Try fuzzy search only if the query is not a digit
            if not query.isdigit():
                fuzzy_results = csvdb.fuzzy_search_item(query)
                if fuzzy_results:
                    len_results = len(fuzzy_results)
                else:
                    await message.channel.send(":woman_shrugging: I could not find any items matching that name, maybe check your spelling?")
                    return

  
        

        # Format the search results
        formatted_results = []
        # Use fuzzy_results if available, otherwise use search_results
        if 'fuzzy_results' in locals() and fuzzy_results:
            results_to_use = fuzzy_results
        else:
            results_to_use = search_results['results']
        
        for index, result in enumerate(results_to_use):
            if 'fuzzy_results' in locals() and fuzzy_results:
                ffxiv_item = result  # Use the FFXIVItem directly from fuzzy_results
            else:
                ffxiv_item = FFXIVItem("", 0, "", "", "")
                if not ffxiv_item.auto_fill_info_from_xivapi(result):
                    continue  # Skip if auto-fill fails
                # Add the item to the CSVDB if it does not exist
                csvdb.update(ffxiv_item)

            if index < 10:  # Only format the first 10 items
                wiki_link = f"https://ffxiv.gamerescape.com/wiki/{ffxiv_item.item_name.replace(' ', '_')}"
                result_text = f"- {ffxiv_item.emoji} {ffxiv_item.item_name} (ID: {ffxiv_item.item_id}) - [Wiki](<{wiki_link}>) | [Universalis](<https://universalis.app/market/{ffxiv_item.item_id}>) | [Garland Tools](<https://garlandtools.org/db/#item/{ffxiv_item.item_id}>)"
                formatted_results.append(result_text)


        
        # Always show the [+] emoji and remaining results message
        if len_results - len(formatted_results) > 1:
            remaining_results_text = f"**{len_results - len(formatted_results)}** more results found."
            formatted_results.append(remaining_results_text)

        await message.add_reaction("🔍")
        
       
        # Create an embed for the search results
        embed = discord.Embed(title="Search Results", description="\n".join(formatted_results), color=0x00ff00)

        if 'fuzzy_results' in locals() and fuzzy_results:
            note_text = f":mag_right: I could not find **{query}** but found some similar items in the database."
            embed.add_field(name="Note", value=note_text, inline=False)


        # Send the embed back to the Discord channel
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send(f"[Main][handle_search_command] An error occurred while searching for items: {e}")




async def handle_price_command(message: discord.Message, item_id: Optional[int] = None, user: Optional[discord.User] = None) -> None:
    """
    Handles the '!price' command from a Discord message. This command allows users to query the market price
    of an item by either its ID or name. The function checks if the user has the required role to execute
    the command, processes the query, and sends an embedded message with the market data.

    Parameters:
    - message (discord.Message): The message object containing the command and its context.
    - item_id (Optional[int]): The optional item ID to search for.

    Returns:
    - None: Sends a message back to the Discord channel with the result or an error message.
    """
    # Assign item_id to query if item_id is set, otherwise extract the query from the message
    query = str(item_id) if item_id is not None else message.content[6:].strip()
    
    # Check if the user has the required role
    if user:
        if not any(role.id == ROLE_ID for role in user.roles):
            await message.channel.send("You do not have permission to use this command.")
            return
    else:
        if not any(role.id == ROLE_ID for role in message.author.roles):
            await message.channel.send("You do not have permission to use this command.")
            return

    # Check if the query is empty
    if not query:
        await message.channel.send("Please provide an item ID or name. Example: `!price 12345` or `!price Dark Matter Cluster`")
        return

    try:
        # Determine if the query is a numeric ID or a name
        if query.isdigit():
            item_id = int(query)
            print(f"[Main][handle_price_command] Searching for item by ID: {item_id}")
            ffxiv_item = csvdb.search_item_by_id(item_id)
        else:
            # Assume single item name
            print(f"[Main][handle_price_command] Searching for item by name: {query}")
            ffxiv_item = csvdb.search_item_by_name(query)


        if not ffxiv_item:
            print(f"[Main][handle_price_command] Attempting fuzzy search for item: {query}")
            fuzzy_results = csvdb.fuzzy_search_item(query)
            ffxiv_item = fuzzy_results[0] if isinstance(fuzzy_results, list) and fuzzy_results else None
            if not ffxiv_item:
                await message.channel.send(":woman_shrugging: I could not find any data for that item, maybe check your spelling?")
                return
            else:
                print(f"[Main][handle_price_command] Fuzzy search found item: {ffxiv_item.item_name} (ID: {ffxiv_item.item_id})")
                fuzzy = True

        print(f"[Main][handle_price_command] Getting market data for {ffxiv_item.item_name} (ID: {ffxiv_item.item_id})")
        # Get market data for the item
        results = get_market_data([str(ffxiv_item.item_id)], message)

        if not results:
            await message.channel.send(":woman_shrugging: I could not find any data for that item, maybe check your spelling?")
            return

        # Process the result
        item = results[0]['results'][0]
   
        nq_data = item["nq"]["minListing"]
        hq_data = item["hq"]["minListing"]
        timedata = item["worldUploadTimes"]

        lowest_timestamp = float('inf')
        lowest_world = None
        for time in timedata:
            if time["timestamp"] < lowest_timestamp:
                lowest_timestamp = time["timestamp"]
                lowest_world = csvdb.search_world_by_id(time["worldId"])

        has_hq_data = bool(hq_data)

        formatted_time = datetime.fromtimestamp(lowest_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')


        # Pre-calculate each group
        world_info = ""
        if 'world' in nq_data:
            world_info = f":coin:{int(nq_data['world']['price']):,} gil"
            if has_hq_data and 'world' in hq_data:
                world_info += f" / :sparkles:{int(hq_data['world']['price']):,} gil"

        datacenter_info = f":coin:{int(nq_data['dc']['price']):,} gil `({csvdb.search_world_by_id(nq_data['dc']['worldId'])})`"
        region_info = f":coin:{int(nq_data['region']['price']):,} gil `({csvdb.search_world_by_id(nq_data['region']['worldId'])})`"
        if has_hq_data:
            region_info += f" / :sparkles:{int(hq_data['region']['price']):,} gil `({csvdb.search_world_by_id(hq_data['region']['worldId'])})`"
            datacenter_info += f" / :sparkles:{int(hq_data['dc']['price']):,} gil `({csvdb.search_world_by_id(hq_data['dc']['worldId'])})`"
  
        # Create an embed
        embed = Embed(title=f"Market Data for {ffxiv_item.emoji} {ffxiv_item.item_name} (ID: {ffxiv_item.item_id})", color=0x00ff00)
        
        embed.add_field(name=":japan: Region", value=region_info, inline=False)
        embed.add_field(name=":office: Datacenter", value=datacenter_info, inline=False)
        if world_info:
            embed.add_field(name=f":earth_americas: World ({SERVER_NAME})", value=world_info, inline=False)
        embed.add_field(name="Links", value=f"[Gamerscape Wiki](<https://ffxiv.gamerescape.com/wiki/{ffxiv_item.item_name.replace(' ', '_')}>) | [Universalis](<https://universalis.app/market/{ffxiv_item.item_id}>) | [Garland Tools](<https://garlandtools.org/db/#item/{ffxiv_item.item_id})")
        embed.set_thumbnail(url=ffxiv_item.icon_url)  # Use the icon URL from the FFXIVItem instance
        embed.set_footer(text=f"Oldest update was on {lowest_world} at {formatted_time}")
        

        if fuzzy:
            embed.add_field(name="Note", value=f":mag_right: I could not find **{query}** but found some similar items in the database.", inline=False)

        # Add a reaction emote to the user's message
        await message.add_reaction("👌")

        await message.channel.send(embed=embed)
    except Exception as e:
        await message.channel.send(f"[Main][handle_price_command] An error occurred while processing your request: {str(e)}")


async def handle_setemoji_command(message: discord.Message) -> None:
    # Check if the user has the required role
    if not any(role.id == ROLE_ID for role in message.author.roles):
        await message.channel.send("You do not have permission to use this command.")
        return

    # Parse the message content to extract item_id and emoji
    try:
        _, item_id, emoji = message.content.split()
    except ValueError:
        await message.channel.send("Invalid command format. Use: `!setemoji <itemid> <emoji>`")
        return

    # Validate item_id
    if not item_id.isdigit():
        await message.channel.send("Item ID must be a number.")
        return

    # Trim colons from emoji if present
    if emoji.startswith(":") and emoji.endswith(":"):
        emoji = emoji[1:-1]

    # Check emoji length
    if len(emoji) > 24:
        await message.channel.send("Emoji name must not exceed 24 characters.")
        return

    # Use csvdb to find the FFXIVItem instance
    ffxiv_item = csvdb.search_item_by_id(int(item_id))

    if ffxiv_item:
        # Set the new emoji
        ffxiv_item.emoji = emoji
        # Update the item in CSVDB
        csvdb.update_item(ffxiv_item)
    else:
        # Inform the user if the item_id is not found in the database
        await message.channel.send("Item ID not found on the database. Maybe search its price first so I can add it?")
        return

    # React to the user's message to indicate success
    await message.add_reaction("📓")
    item_name = ffxiv_item.item_name

    # Notify the user of the successful update
    await message.channel.send(f"Emoji for item ID {item_id} ({item_name}) has been updated to {emoji}.")



@bot.event
async def on_reaction_add(reaction, user):
    """
    Event handler for when a reaction is added to a message.
    If the reaction is the money emoji, it will trigger the handle_price_command.
    If the reaction is the book emoji, it will show the full recipe.
    
    Parameters:
    - reaction (discord.Reaction): The reaction object containing the emoji and message.
    - user (discord.User): The user who added the reaction.
    """
    # Get the message that was reacted to
    message = reaction.message

    # Check if the reaction is the money emoji and the user is not the bot itself
    if reaction.emoji == "💰" and user != bot.user:

        # Check if the bot has already reacted with the hand OK emoji
        if any(reaction.emoji == "👌" and reaction.me for reaction in message.reactions):
            return

        # Check if the message was sent by the bot
        if message.author == bot.user:
            # Extract the item ID from the message embed
            if message.embeds:
                embed = message.embeds[0]
                title = embed.title
                if title and "ID:" in title:
                    # Extract the item ID from the title
                    item_id = int(title.split("ID:")[1].split(")")[0].strip())

                    # Call handle_price_command with the extracted item ID
                    await handle_price_command(message, item_id, user)

    # Check if the reaction is the book emoji and the user is not the bot itself
    elif reaction.emoji == "📓" and user != bot.user:


        # Check if the message was sent by the bot
        if message.author == bot.user and any(reaction.emoji == "📖" and reaction.me for reaction in message.reactions):
            return
        # Extract the item ID from the message embed
        if message.embeds:
            embed = message.embeds[0]
            title = embed.title
            if title and "ID:" in title:
                # Extract the item ID from the title
                item_id = int(title.split("ID:")[1].split(")")[0].strip())

                # Search for the recipe using the item ID
                recipe = csvdb.search_recipes_by_item_id(item_id)

                # Call a function to show the full recipe with the extracted item ID
                if recipe:
                    await handle_recipe_command(message, recipe_id=item_id, full_recipe=True)
        


def main():
   
    try:
        # Attempt to run the bot with the provided token
        bot.run(TOKEN)  # Replace with your bot token
    except discord.LoginFailure:
        # Handle the case where the provided token is invalid
        print("[Main] Invalid token provided. Please check your bot token.")
    except Exception as e:
        # Handle any other exceptions that may occur
        print(f"[Main] An error occurred: {e}")
if __name__ == "__main__":
    main()