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
from classes.recipe import Recipe

# Discord imports
import discord
from discord.ext import commands
from discord import Embed

# Official imports
import requests
from datetime import datetime
from typing import Optional
import configparser

class Tataru:
    def __init__(self, config_path='config.ini', testing_mode=False):
        """
        Initialize the Tataru bot with configuration and required setup
        
        Parameters:
        - config_path (str): Path to the configuration file (default: 'config.ini')
        """
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Load configuration values
        self.ROLE_ID = self.config.getint('discord', 'role_id')
        self.SERVER_NAME = self.config['ffxiv']['server']
        self.TOKEN = self.config['discord']['token']
        
        # Initialize database
        self.csvdb = CSVDB()
        
        if not testing_mode:
            # Set up bot intents
            self.intents = discord.Intents.default()
            self.intents.voice_states = False
            self.intents.message_content = True
            
            # Initialize bot with prefix and intents
            self.bot = commands.Bot(command_prefix='!', intents=self.intents)
            
            # Set up event handlers
            self.setup_event_handlers()
        
        print("[Tataru] Initialization complete")

    def setup_event_handlers(self):
        """Set up all the event handlers for the bot"""
        @self.bot.event
        async def on_message(message):
            await self._on_message(message)

        @self.bot.event
        async def on_reaction_add(reaction, user):
            await self._on_reaction_add(reaction, user)

    async def _on_message(self, message: discord.Message) -> None:
        """Event handler for messages"""
        if message.author == self.bot.user:
            return

        if message.content.lower().startswith('!price'):
            await self.handle_price_command(message)
        elif message.content.lower().startswith('!setemoji'):
            await self.handle_setemoji_command(message)
        elif message.content.lower().startswith('!search'):
            await self.handle_search_command(message)
        elif message.content.lower().startswith('!recipe'):
            await self.handle_recipe_command(message)

    async def _on_reaction_add(self, reaction, user):
        """Event handler for reaction adds"""
        message = reaction.message

        if reaction.emoji == "💰" and user != self.bot.user:
            if any(reaction.emoji == "👌" and reaction.me for reaction in message.reactions):
                return

            if message.author == self.bot.user:
                if message.embeds:
                    embed = message.embeds[0]
                    title = embed.title
                    if title and "ID:" in title:
                        item_id = int(title.split("ID:")[1].split(")")[0].strip())
                        await self.handle_price_command(message, item_id, user)

        elif reaction.emoji == "📓" and user != self.bot.user:
            if message.author == self.bot.user and any(reaction.emoji == "📖" and reaction.me for reaction in message.reactions):
                return
            if message.embeds:
                embed = message.embeds[0]
                title = embed.title
                if title and "ID:" in title:
                    item_id = int(title.split("ID:")[1].split(")")[0].strip())
                    recipe = self.csvdb.search_recipes_by_item_id(item_id)
                    if recipe:
                        await self.handle_recipe_command(message, recipe_id=item_id, full_recipe=True)

    def get_market_data(self, item_ids: list, message: discord.Message) -> list:
        """Get market data for specified item IDs from Universalis API"""
        results = []
        base_url = f"https://universalis.app/api/v2/aggregated/{self.SERVER_NAME}/"

        print(f"[Tataru][get_market_data] Fetching market data for {item_ids} requested by {message.author}")

        try:
            items_string = ",".join(map(str, item_ids))
            url = f"{base_url}{items_string}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "items" in data:
                results = data["items"]
            else:
                results = [data]

            print(f"[Tataru][get_market_data] Market data fetched for {item_ids} requested by {message.author}")
            return results

        except requests.RequestException as e:
            print(f"[Tataru][get_market_data] Error fetching market data: {e}")
            return []
        except ValueError as e:
            print(f"[Tataru][get_market_data] Error parsing response: {e}")
            return []
        except Exception as e:
            print(f"[Tataru][get_market_data] Unexpected error: {e}")
            return []

    async def create_recipe_embed(self, item: FFXIVItem, all_ingredients=False, craftType=None, recipe_amount=1, hide_reactions=False) -> discord.Embed:
        """Create an embed for recipe information"""
        embed = Embed(title=f"Recipe for {recipe_amount}x {item.emoji}{item.item_name} (ID: {item.item_id})", color=0x00ff00)
        embed.set_thumbnail(url=item.icon_url)
        embed.add_field(name="Wiki", value=f"[Link](https://ffxiv.gamerescape.com/wiki/{item.item_name.replace(' ', '_')})", inline=True)
        embed.add_field(name="Universalis", value=f"[Link](https://universalis.app/market/{item.item_id})", inline=True)
        embed.add_field(name="Garland Tools", value=f"[Link](https://www.garlandtools.org/db/#item/{item.item_id})", inline=True)
        embed.add_field(name="Craft Type", value=craftType if craftType else item.category, inline=True)

        full_ingredients_list = ""
        if all_ingredients:
            crystal_ingredients = ""
            non_crystal_ingredients = ""

            for ingredient_id, amount in all_ingredients.items():
                ingredient_item = self.csvdb.search_item_by_id(ingredient_id)
                ingredient = (
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

    def get_recipe_ingredients(self, recipe: Recipe, recursive=False, multiplier=1):
        """Get all ingredients required for a recipe"""
        ingredients = {}
        
        for i in range(8):
            ingredient = recipe.get_ingredient_by_index(i)
            if ingredient and ingredient['itemID'] > 0:
                ingredient_id = ingredient['itemID']
                amount_needed = ingredient['amount'] * multiplier
                
                if recursive:
                    sub_recipes = self.csvdb.search_recipes(ingredient_id)
                    
                    if sub_recipes:
                        sub_recipe = sub_recipes[0]
                        items_per_craft = sub_recipe.amount
                        crafts_needed = (amount_needed + items_per_craft - 1) // items_per_craft
                        sub_ingredients = self.get_recipe_ingredients(sub_recipe, recursive=True, multiplier=crafts_needed)
                        
                        for sub_id, sub_amount in sub_ingredients.items():
                            ingredients[sub_id] = ingredients.get(sub_id, 0) + sub_amount
                    else:
                        ingredients[ingredient_id] = ingredients.get(ingredient_id, 0) + amount_needed
                else:
                    ingredients[ingredient_id] = ingredients.get(ingredient_id, 0) + amount_needed

        return ingredients

    async def handle_recipe_command(self, message: discord.Message, recipe_id: int = -1, full_recipe: bool = False) -> None:
        """Handle the !recipe command"""
        if recipe_id == -1:
            item_identifier = message.content[7:].strip()
            if not item_identifier:
                await message.channel.send("Please provide an item name or ID to get the recipe for. Example: `!recipe Dark Matter`")
                return
        else:
            item_identifier = recipe_id

        recipes = self.csvdb.search_recipes(item_identifier)

        if recipes:
            recipe = recipes[0]
            item = self.csvdb.search_item_by_id(recipe.itemID)
            
            if item:
                if full_recipe:
                    await message.add_reaction("📖")

                all_ingredients = self.get_recipe_ingredients(recipe, recursive=full_recipe)
                embed = await self.create_recipe_embed(item, all_ingredients, recipe.get_craftTypeName(), recipe.amount, hide_reactions=full_recipe)
            else:
                await message.channel.send(f"Failed to fetch item details for {item_identifier}")
                return
            
            sent_message = await message.channel.send(embed=embed)
            
            if not full_recipe:
                await sent_message.add_reaction("💰")
                await sent_message.add_reaction("📓")
        else:
            await message.channel.send(f"No recipe found for {item_identifier}")

    async def handle_search_command(self, message: discord.Message) -> None:
        """Handle the !search command"""
        query = message.content[8:].strip()
        if not query:
            await message.channel.send("Please provide an item name to search for. Example: `!search Dark Matter`")
            return

        try:
            search_results = self.csvdb.xivapi.item_search(query)
            len_results = len(search_results['results'])
            if not search_results['results']:
                if not query.isdigit():
                    fuzzy_results = self.csvdb.fuzzy_search_item(query)
                    if fuzzy_results:
                        len_results = len(fuzzy_results)
                    else:
                        await message.channel.send(":woman_shrugging: I could not find any items matching that name, maybe check your spelling?")
                        return

            formatted_results = []
            if 'fuzzy_results' in locals() and fuzzy_results:
                results_to_use = fuzzy_results
            else:
                results_to_use = search_results['results']
            
            for index, result in enumerate(results_to_use):
                if 'fuzzy_results' in locals() and fuzzy_results:
                    ffxiv_item = result
                else:
                    ffxiv_item = FFXIVItem("", 0, "", "", "")
                    if not ffxiv_item.auto_fill_info_from_xivapi(result):
                        continue
                    self.csvdb.update(ffxiv_item)

                if index < 10:
                    wiki_link = f"https://ffxiv.gamerescape.com/wiki/{ffxiv_item.item_name.replace(' ', '_')}"
                    result_text = (
                        f"- {ffxiv_item.emoji} {ffxiv_item.item_name} "
                        f"(ID: {ffxiv_item.item_id}) - "
                        f"[Wiki](<{wiki_link}>) | "
                        f"[Universalis](<https://universalis.app/market/{ffxiv_item.item_id}>) | "
                        f"[Garland Tools](<https://garlandtools.org/db/#item/{ffxiv_item.item_id}>)"
                    )
                    formatted_results.append(result_text)

            if len_results - len(formatted_results) > 1:
                remaining_results_text = f"**{len_results - len(formatted_results)}** more results found."
                formatted_results.append(remaining_results_text)

            await message.add_reaction("🔍")
            
            embed = discord.Embed(title="Search Results", description="\n".join(formatted_results), color=0x00ff00)

            if 'fuzzy_results' in locals() and fuzzy_results:
                note_text = f":mag_right: I could not find **{query}** but found some similar items in the database."
                embed.add_field(name="Note", value=note_text, inline=False)

            await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send(f"[Tataru][handle_search_command] An error occurred while searching for items: {e}")

    async def handle_price_command(self, message: discord.Message, item_id: Optional[int] = None, user: Optional[discord.User] = None) -> None:
        """Handle the !price command"""
        query = str(item_id) if item_id is not None else message.content[6:].strip()
        fuzzy = False

        if user:
            if not any(role.id == self.ROLE_ID for role in user.roles):
                await message.channel.send("You do not have permission to use this command.")
                return
        else:
            if not any(role.id == self.ROLE_ID for role in message.author.roles):
                await message.channel.send("You do not have permission to use this command.")
                return

        if not query:
            await message.channel.send("Please provide an item ID or name. Example: `!price 12345` or `!price Dark Matter Cluster`")
            return

        try:
            if query.isdigit():
                item_id = int(query)
                ffxiv_item = self.csvdb.search_item_by_id(item_id)
            else:
                ffxiv_item = self.csvdb.search_item_by_name(query)

            if not ffxiv_item:
                fuzzy_results = self.csvdb.fuzzy_search_item(query)
                ffxiv_item = fuzzy_results[0] if isinstance(fuzzy_results, list) and fuzzy_results else None
                if not ffxiv_item:
                    await message.channel.send(":woman_shrugging: I could not find any data for that item, maybe check your spelling?")
                    return
                fuzzy = True

            results = self.get_market_data([str(ffxiv_item.item_id)], message)

            if not results:
                await message.channel.send(":woman_shrugging: I could not find any data for that item, maybe check your spelling?")
                return

            item = results[0]['results'][0]
            nq_data = item["nq"]["minListing"]
            hq_data = item["hq"]["minListing"]
            timedata = item["worldUploadTimes"]

            lowest_timestamp = float('inf')
            lowest_world = None
            for time in timedata:
                if time["timestamp"] < lowest_timestamp:
                    lowest_timestamp = time["timestamp"]
                    lowest_world = self.csvdb.search_world_by_id(time["worldId"])

            has_hq_data = bool(hq_data)
            formatted_time = datetime.fromtimestamp(lowest_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

            world_info = ""
            if 'world' in nq_data:
                world_info = f":coin:{int(nq_data['world']['price']):,} gil"
                if has_hq_data and 'world' in hq_data:
                    world_info += f" / :sparkles:{int(hq_data['world']['price']):,} gil"
                world_info += f" `({self.SERVER_NAME})`"

            datacenter_info = f":coin:{int(nq_data['dc']['price']):,} gil `({self.csvdb.search_world_by_id(nq_data['dc']['worldId'])})`"
            region_info = f":coin:{int(nq_data['region']['price']):,} gil `({self.csvdb.search_world_by_id(nq_data['region']['worldId'])})`"
            
            if has_hq_data:
                region_info += f" / :sparkles:{int(hq_data['region']['price']):,} gil `({self.csvdb.search_world_by_id(hq_data['region']['worldId'])})`"
                datacenter_info += f" / :sparkles:{int(hq_data['dc']['price']):,} gil `({self.csvdb.search_world_by_id(hq_data['dc']['worldId'])})`"

            embed = Embed(title=f"Market Data for {ffxiv_item.emoji} {ffxiv_item.item_name} (ID: {ffxiv_item.item_id})", color=0x00ff00)
            embed.add_field(name=":japan: Region", value=region_info, inline=False)
            embed.add_field(name=":office: Datacenter", value=datacenter_info, inline=False)
            if world_info:
                embed.add_field(name=f":earth_americas: World", value=world_info, inline=False)
            embed.add_field(name="Links", value=f"[Gamerscape Wiki](<https://ffxiv.gamerescape.com/wiki/{ffxiv_item.item_name.replace(' ', '_')}>) | [Universalis](<https://universalis.app/market/{ffxiv_item.item_id}>) | [Garland Tools](<https://garlandtools.org/db/#item/{ffxiv_item.item_id}>)")
            embed.set_thumbnail(url=ffxiv_item.icon_url)
            embed.set_footer(text=f"Oldest update was on {lowest_world} at {formatted_time}")

            if fuzzy:
                embed.add_field(name="Note", value=f":mag_right: I could not find **{query}** but found some similar items in the database.", inline=False)

            await message.add_reaction("👌")
            await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send(f"[Tataru][handle_price_command] An error occurred while processing your request: {str(e)}")

    async def handle_setemoji_command(self, message: discord.Message) -> None:
        """Handle the !setemoji command"""
        if not any(role.id == self.ROLE_ID for role in message.author.roles):
            await message.channel.send("You do not have permission to use this command.")
            return

        try:
            _, item_id, emoji = message.content.split()
        except ValueError:
            await message.channel.send("Invalid command format. Use: `!setemoji <itemid> <emoji>`")
            return

        if not item_id.isdigit():
            await message.channel.send("Item ID must be a number.")
            return

        if emoji.startswith(":") and emoji.endswith(":"):
            emoji = emoji[1:-1]

        if len(emoji) > 24:
            await message.channel.send("Emoji name must not exceed 24 characters.")
            return

        ffxiv_item = self.csvdb.search_item_by_id(int(item_id))

        if ffxiv_item:
            ffxiv_item.emoji = emoji
            self.csvdb.update(ffxiv_item)
        else:
            await message.channel.send("Item ID not found on the database. Maybe search its price first so I can add it?")
            return

        await message.add_reaction("📓")
        await message.channel.send(f"Emoji for item ID {item_id} ({ffxiv_item.item_name}) has been updated to {emoji}.")

    def run(self):
        """Start the bot"""
        try:
            self.bot.run(self.TOKEN)
        except discord.LoginFailure:
            print("[Tataru] Invalid token provided. Please check your bot token.")
        except Exception as e:
            print(f"[Tataru] An error occurred: {e}")

if __name__ == "__main__":
    tataru = Tataru()
    tataru.run()
