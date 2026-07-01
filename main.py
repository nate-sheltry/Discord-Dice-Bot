import settings
import discord
import hashlib
import random
import time
import json
from aiohttp import web
from typing import Literal
from discord.ext import commands
from text_formatting import text_methods as Tm
import re
import os

current_time = 0
random.seed(current_time)

SUBDIRECTORY = 'guilds_data'
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
karmic = [True]

logger = settings.logging.getLogger("bot")

guilds = {}

player_rolls = {}

user_names = {}

# WebService Uptime
async def health_check(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

#Methods/Functions for Program Use
def hash_string(string):
    sha256 = hashlib.sha256()
    sha256.update(f'{settings.PREHASH}{string}'.encode('utf-8'))
    hash_result = sha256.hexdigest()
    return hash_result

def set_random_seed():
    current_time = int(time.time())
    random.seed(current_time)

def exit_handler(ctx, data, guild_id):
    directory = os.path.join(SCRIPT_DIRECTORY, SUBDIRECTORY)
    os.makedirs(directory, exist_ok=True)
    with open(f'{directory}/{guild_id}.json', 'w') as file:
        json.dump(data, file)

def load_names():
    directory = os.path.join(SCRIPT_DIRECTORY, SUBDIRECTORY)
    os.makedirs(directory, exist_ok=True)
    filelist = os.listdir(directory)
    empty_dict = {}
    for file in filelist:
        try:
            with open(f'{directory}/{file}', "r") as f:
                empty_dict[file.replace(".json", "")] = json.load(f)
        except Exception:
            return None
    return empty_dict

async def process_roll(input_text):
    try:
        space_string = ''
        components = re.split(r'([+-])', input_text)
        space_string = ''.join(components)
        if(' ' in input_text):
            components = re.split(r'\s', input_text)
            space_string = ''.join(components)
            components = re.split(r'([+-])', space_string)
        
        
        dice = []
        operators = []
        modifiers = []
        
        for comp in components:
            if comp in ('+', '-'):
                operators.append(comp)
            else:
                match = re.match(r'(\d*)d(\d+)', comp)
                if match:
                    num_dice = int(match.group(1) or 1)
                    dice_sides = int(match.group(2))
                    dice.append((num_dice, dice_sides))
                else:
                    value = comp
                    operator = operators.pop(len(operators)-1)
                    modifiers.append((operator, int(value)))
        
        print(f'Dice: {dice}')
        print(f'Operators: {operators}')
        if(len(modifiers) > 0):
            print(f'Modifiers: {modifiers}')
        
        return dice, operators, modifiers
    except:
        return None, None, None,

def roll_die(player_id, max_num, min_num=1):
    roll = random.randint(min_num, max_num)
    if(max_num != 20):
        return roll
    if(karmic[0] == False):
        return
    if(player_id in player_rolls.keys()):
        player_dict = player_rolls[player_id]
    else:
        player_dict = {'value1': 0, 'value2': 0, 'value3': 0}
        player_rolls[player_id] = player_dict
        
    if(roll == 1):
        #if it rolls a one, re-roll, we don't want crit fails.
        if(player_dict['value1'] == 1 and player_dict['value2'] == 1):
            #Do not allow 3 crit failures in a row
            while(roll == 1):
                roll = random.randint(min_num, max_num)
        elif(roll == player_dict['value1']):
            #if you just rolled a 1 last roll, reroll it twice to get decrease the chance of getting a 1.
            roll = random.randint(min_num, max_num)
            if(roll == 1):
                roll = random.randint(min_num, max_num)
                
    elif(roll == 20):
        if(player_dict['value1'] == 20 and player_dict['value2'] == 20 and player_dict['value3'] == 20):
            #do not allow 4 crits
            while(roll == 20):
                roll = random.randint(min_num, max_num)
        elif(player_dict['value1'] == 20 and player_dict['value2'] == 20):
            roll = random.randint(min_num, max_num)
    
    elif(roll == player_dict['value1'] and roll == player_dict['value2']):
        while(roll == player_dict['value1']):
                roll = random.randint(min_num, max_num)
    elif(roll == player_dict['value2'] and roll == player_dict['value3']):
        roll = random.randint(min_num, max_num)
    
    player_rolls[player_id]['value3'] = player_rolls[player_id]['value2']
    player_rolls[player_id]['value2'] = player_rolls[player_id]['value1']
    player_rolls[player_id]['value1'] = roll
    return roll

def roll_dice(player_id, dice):
    dice_rolled = []
    for i in range(dice[0]):
        dice_rolled.append(roll_die(player_id, dice[1]))
    return dice_rolled

async def delete_message(ctx):
    if ctx.interaction is not None:
        return
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    except discord.Forbidden:
        logger.warning(f"Missing permissions to delete in {ctx.channel}")

async def get_name(ctx):
    user_name = 'None'
    guild_id = str(ctx.guild.id)
    guild_id_hash = hash_string(guild_id)
    try:
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        if(guild_id_hash in guilds):
            if(user_id_hash in guilds.get(guild_id_hash)):
                return f'{guilds.get(guild_id_hash).get(user_id_hash)}'
        if user_name == 'None':
            user_name = ctx.author.nick
            if str(user_name) == 'None':
                user_name = ctx.author.name
    except AttributeError:
        user_id = str(ctx.user.id)
        user_id_hash = hash_string(user_id)
        if(guild_id_hash in guilds):
            if(user_id_hash in guilds.get(guild_id_hash)):
                return f'{guilds.get(guild_id_hash).get(user_id_hash)}'
        if user_name == 'None':
            user_name = ctx.user.nick
            if str(user_name) == 'None':
                user_name = ctx.user.name
    return user_name


async def display_emphasized_roll(ctx, dice, rolls_array):
    message = ''
    name = Tm.bold_italics(await get_name(ctx))
    message += f'{name} rolled d20 Emphasized:\n===========================================================\n'
    message += '>  ' + f'{Tm.bold("Emphasized Roll:")}\n'
    message += '>  (' + f'\t{rolls_array[0]}\t' + f') \t {Tm.bold(str(abs(rolls_array[0]-10)))} from {Tm.bold("10")}  \n'
    message += '>  (' + f'\t{rolls_array[1]}\t' + f') \t {Tm.bold(str(abs(rolls_array[1]-10)))} from {Tm.bold("10")}  \n'
    message += '>  ' + f'------------------------------\n'
    message += f'   {Tm.inline_code("Result")}: {Tm.bold_italics(dice)}'
    try:
        await ctx.send(message)
    except AttributeError:
        await ctx.response.send_message(message)
    
    

async def display_roll(ctx, what, dice, operators, modifiers, adv=False, dis=False, rolls_array=[]):
    total = 0
    temp_array = []
    message = ''
    dice_message = ''
    modifier_total = 0
    
    name = Tm.bold_italics(await get_name(ctx))
    roll = Tm.inline_code(what)
    
    if(adv == False and dis == False):
        message += f'## {name} rolled {roll}:\n'
    elif(adv == True):
        message += f'## {name} rolled with Advantage {roll}:\n'
    elif(dis == True):
        message += f'## {name} rolled with Disadvantage {roll}:\n'
    
    #display total
    for i in range(len(dice)):
        if(adv or dis):
            if(i == 0):
                if(adv):dice_message += '>  ' + f'{Tm.bold("Advantage Die:")}\n'
                else:dice_message += '>  ' + f'{Tm.bold("Disadvantage Die:")}\n'
                for value in rolls_array:
                    logger.info('Rolls Array Value:' + f'{value}')
                    dice_message += '>  ('
                    for x in range(len(value)):
                        logger.info('Rolls Array Value-in-Value:' + f'{value[x]}')
                        if(x > 0):
                            dice_message += ' + '
                        dice_message += f'\t{value[x]}\t'
                        if(x == len(value)-1):
                            dice_message += ') \t = \t'
                    dice_message += f'{sum(value)}\n'
                dice_message += '>  ' + f'------------------------------\n'
                dice_message += Tm.block_quote(f' {Tm.inline_code("Result Die")}: {Tm.bold_italics(sum(dice[i]))}\n>  \n')
                continue
        else:
            if(i == 0):
                dice_message += '>  ' + f'{Tm.bold("Standard Roll:")}\n'
        if(i == 1):dice_message += '>  ' + f'{Tm.bold("Modifier Dice:")}\n'
        dice_message += '>  ('
        for x in range(len(dice[i])):
            if(x > 0):
                dice_message += ' + '
            dice_message += f'\t{dice[i][x]}\t'
            if(x == len(dice[i]) -1):
                dice_message += ') \t = \t'
        if(i != 0):
            dice_message += operators[i-1]
        dice_message += f'{sum(dice[i])}\n'
    dice_message += '>  ' + f'------------------------------\n'
    
    
    #compute total
    for i in range(len(dice)):
        temp_array.append(sum(dice[i]))
    
    total = temp_array[0]
    for i in range(len(operators)):
        if(operators[i] == '+'):
            total += temp_array[i+1]
        if(operators[i] == '-'):
            total -=  temp_array[i+1]
    
    logger.info(temp_array)
    
    # dice_message += Tm.block_quote(f' {Tm.inline_code("Total Dice Modifier")}: {Tm.bold_italics(total-temp_array[0])}\n>  \n')
    if(len(modifiers) > 0):
        dice_message += '>  ' + f'{Tm.bold("Modifiers:")}\n'
        dice_message += '>  ('
        
        for i in range(len(modifiers)):
            modifier = modifiers[i]
            if('+' in modifier[0]):
                modifier_total += modifier[1]
                if(i == 0):dice_message += f' {modifier[1]} '
                else:dice_message += f'\t {modifier[0]} \t {modifier[1]}'
            elif('-' in modifier[0]):
                modifier_total -= modifier[1]
                if(i == 0):dice_message += f' {modifier[0]}{modifier[1]} '
                else:dice_message += f'\t {modifier[0]} \t {modifier[1]} '
        dice_message += ')\n'
        dice_message += '>  ' + f'------------------------------\n'
        dice_message += Tm.block_quote(f' {Tm.inline_code("Modifiers Total")}: {Tm.bold_italics(f"{modifier_total}")}\n')
    message += dice_message
    
    message += (f'### {Tm.inline_code("Total")}: {Tm.bold_italics(f"{total+modifier_total}")}\t')
    if(len(modifiers) > 0):
        message += Tm.inline_code(f'Natural Roll Value') + f': {Tm.bold_italics(temp_array[0])}'
    try:
        await ctx.send(message)
    except AttributeError:
        await ctx.response.send_message(message)

#Program Run/Commands and Events
    
def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix=["!", "\\"], intents=intents)
    
    #On load Event
    @bot.event
    async def on_ready():
        data = load_names()
        if data:
            guilds.update(data)
        logger.info(f"(User: {bot.user}) (ID: {bot.user.id})")
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
        bot.loop.create_task(start_web_server())
        
    @bot.hybrid_command(
        name="karmic-setting",
        aliases=['switchKarmic', 'sK', 'SK', 'Sk'],
        help="Entering this command will disable or Enable Karmic Dice for D20 rolls, !sk",
        description="Set whether the d20 dice should mitigating outlier rolls.",
        brief="Switch whether dice are Karmic or Not."
    )
    async def sk(ctx, mode: Literal["On", "Off"]):
        if mode == None:
            if karmic[0]:
                karmic[0] = False
            elif karmic[0] == False:
                karmic[0] = True
        else:
            if(mode == "On"):
                karmic[0] = True
            elif(mode == "Off"):
                karmic[0] = False
        await ctx.send(f"The Karmic setting is set to {karmic[0]}.")
    
    @bot.command(
        aliases=['displayData'],
        help_message="Displays Server, Server ID Hash, and users with data. !disData"
    )
    async def disDat(ctx):
        guild_id = str(ctx.guild.id)
        guild_id_hash = hash_string(guild_id)
        await ctx.send('Number of users with stored data.')
        amount = 0
        try:
            amount = len(guilds.get(guild_id_hash).keys())
        except Exception:
            amount = 0
        await ctx.send(Tm.block_quote(amount))
        await ctx.send(Tm.bold('Guild: ') + Tm.italics(str(ctx.guild.name)))
        await ctx.send(Tm.bold('Guild ID: ') + Tm.italics(str(guild_id_hash)))
        await ctx.send(Tm.bold('Karmic Setting: ') + Tm.italics(f'{karmic[0]}'))
    
    @bot.tree.command(
        name="set-name",
        description="Sets a custom name for rolls."
    )
    async def setName(interaction, name:str):
        guild_id = str(interaction.guild.id)
        guild_id_hash = hash_string(guild_id)
        user_id = str(interaction.user.id)
        user_id_hash = hash_string(user_id)
        guilds.update({guild_id_hash: {user_id_hash: name} })
        exit_handler(interaction, guilds, guild_id_hash)
        await interaction.response.send_message(f'{interaction.user.name} set their Name to {guilds.get(guild_id_hash).get(user_id_hash)}')
    
    @bot.command(
        aliases=["setName","SN"],
        help="Set a custom name for the bot to use. !sn name",
        description="Allows a user to",
        brief="Brief Message"
    )
    async def sn(ctx, name):
        guild_id = str(ctx.guild.id)
        guild_id_hash = hash_string(guild_id)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        guilds.update({guild_id_hash: {user_id_hash: name} })
        exit_handler(ctx, guilds, guild_id_hash)
        await delete_message(ctx)
        await ctx.send(f'{ctx.author.name} set their Name to {guilds.get(guild_id_hash).get(user_id_hash)}')
    
    #Roll Slash Command
    @bot.tree.command(
        name="roll",
        description="roll some dice.",
    )
    async def roll(interaction, number_of_dice:Literal[1,2,3,4,5,6,7,8,9,10], die:Literal[2,3,4,6,8,10,12,20,100]):
        set_random_seed()
        user = await get_name(interaction)
        user_id = str(interaction.user.id)
        user_id_hash = hash_string(user_id)
        if number_of_dice < 1 or die < 2:
            await interaction.response.send_message("Dice count must be at least 1 and Dice sides at least 2.", ephemeral=True)
            return
        
        what = f'{number_of_dice}d{die}'
        dice, operators, modifiers = await process_roll(what)
        result = {"value": []}
        for d in dice:
            result['value'].append(roll_dice(user_id_hash, d))
        await display_roll(interaction, what, result['value'], operators, modifiers)
        
    #Roll Command
    @bot.command(
        aliases=["R"],
        help="Roll's the specified dice with a potential modifier, !r 2d20 + 5",
        description="Rolls the following specified dice, may add or subtract withe dice or integers.\n",
        brief="Roll dice, modify your main dice roll and add a modifier."
    )
    async def r(ctx, *, dice_string):
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        if("d" in dice_string):
            dice, operators, modifiers = await process_roll(dice_string)
            if(dice == operators == modifiers == None):
                return
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            await delete_message(ctx)
            await display_roll(ctx, dice_string, result['value'], operators, modifiers)
                
            
    #Roll with Advantage
    @bot.command(
        aliases=["RA", "rollAdvantage", "rAdv", "rad", "rAd", "radv"],
        help="The same as the !roll command, except it will roll the first dice type with advantage. !ra d20+4 + 1",
        description="Syntax is the same as the !roll command, however it will roll the first die specified twice\ntaking the higher of the two results.",
        brief="Rolls the dice with advantage,and can be modified with other dice ......"
    )
    async def ra(ctx, *, what):
        """Answers with pong"""
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        array = []
        if("d" in what):
            dice, operators, modifiers = await process_roll(what)
            if(dice == operators == modifiers == None):
                return
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            result1 = result['value'][0]
            result2 = roll_dice(user_id_hash, dice[0])
            if sum(result1) > sum(result2):
                result['value'][0] = result1
            elif sum(result1) < sum(result2) or sum(result1) == sum(result2):
                result['value'][0] = result2
            await delete_message(ctx)
            await display_roll(ctx, what, result['value'], operators, modifiers, adv=True, rolls_array=[result1, result2])
    
    #Roll with Disadvantage
    @bot.command(
        aliases=["Rd","rollDisadvantage", "rDis", "rdis", "rDs", "rds"],
        help="Same as the !roll command except rolls first die with disadvantage. !rd d20 - 5",
        description="Rolls the first die twice, and takes the lowest result. Can still be modified by adding additional dice and a modifier.",
        brief="Rolls the dice with disadvantage."
    )
    async def rd(ctx, *, what):
        """Answers with pong"""
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        array = []
        if("d" in what):
            dice, operators, modifiers = await process_roll(what)
            if(dice == operators == modifiers == None):
                return
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            result1 = result['value'][0]
            result2 = roll_dice(user_id_hash, dice[0])
            
            if sum(result1) < sum(result2):
                result['value'][0] = result1
            elif sum(result1) > sum(result2) or sum(result1) == sum(result2):
                result['value'][0] = result2
            await delete_message(ctx)
            await display_roll(ctx, what, result['value'], operators, modifiers, dis=True, rolls_array=[result1, result2])
    
    #Roll with Disadvantage
    @bot.command(
        aliases=["rollEmphasized", "rEm", "rem", "Re", "rE"],
        help="Same as the !roll command except rolls first die with disadvantage. !rd d20 - 5",
        description="Rolls the first die twice, and takes the lowest result. Can still be modified by adding additional dice and a modifier.",
        brief="Rolls the dice with disadvantage."
    )
    async def re(ctx):
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        while(True):
            result1 = roll_die(user_id_hash, 20)
            result2 = roll_die(user_id_hash, 20)
            if(abs(result1 - 10) > abs(result2 - 10)):
                result['value'] = result1
            elif(abs(result1 - 10) < abs(result2 - 10)):
                result['value'] = result2
            if(abs(result1 - 10) != abs(result2 - 10)):
                break
            
        await delete_message(ctx)
        await display_emphasized_roll(ctx, result['value'], [result1, result2])
    
    @bot.command(
        aliases=["input", "test", "inputTest", "IT", "it"],
        help="test for new way of receiving commands",
    )
    async def iT(ctx, *, input_text):
        await ctx.send(input_text)
        

    bot.run(settings.DISCORD_API_TOKEN, root_logger=True)

if __name__ == "__main__":
    run()