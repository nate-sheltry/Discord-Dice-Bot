import settings
import discord
import hashlib
import random
import time
import json
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
    with open(f'{SUBDIRECTORY}/{guild_id}.json', 'w') as file:
        json.dump(data, file)

def load_names():
    directory = os.path.join(SCRIPT_DIRECTORY, SUBDIRECTORY)
    filelist = os.listdir(directory)
    empty_dict = {}
    for file in filelist:
        try:
            with open(f'{directory}/{file}', "r") as f:
                empty_dict[file.replace(".json", "")] = json.load(f)
        except Exception:
            return None
    return empty_dict

async def process_roll(ctx, author, what, adv = False, dis = False):
    components = re.split(r'([+-])', what)
    
    dice = []
    operators = []
    
    for comp in components:
        if comp in ('+', '-'):
            operators.append(comp)
        else:
            match = re.match(r'(\d*)d(\d+)', comp)
            if match:
                num_dice = int(match.group(1) or 1)
                dice_sides = int(match.group(2))
                dice.append((num_dice, dice_sides))
    return dice, operators

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
    await ctx.message.delete()

async def get_name(ctx):
    user_name = 'None'
    guild_id = str(ctx.guild.id)
    guild_id_hash = hash_string(guild_id)
    user_id = str(ctx.author.id)
    user_id_hash = hash_string(user_id)
    if(guild_id_hash in guilds):
        if(user_id_hash in guilds.get(guild_id_hash)):
            return f'{guilds.get(guild_id_hash).get(user_id_hash)}'
    if user_name == 'None':
        print('get nickname')
        user_name = ctx.author.nick
        logger.info(f"Nick Name: {ctx.author.nick}")
        if str(user_name) == 'None':
            user_name = ctx.author.name
            logger.info(f"Name: {ctx.author.name}")
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
    await ctx.send(message)
    
    

async def display_roll(ctx, what, dice, operators, modifier, integer, adv=False, dis=False, rolls_array=[]):
    
    total = 0
    temp_array = []
    message = ''
    dice_message = ''
    print('Display Roll Executed')
    logger.info('Rolls Array:' + f'{rolls_array}')
    
    name = Tm.bold_italics(await get_name(ctx))
    roll = Tm.inline_code(what)
    
    if(adv == False and dis == False):
        message += f'{name} rolled {roll}:\n===========================================================\n'
    elif(adv == True):
        message += f'{name} rolled with Advantage {roll}:\n===========================================================\n'
    elif(dis == True):
        message += f'{name} rolled with Disadvantage {roll}:\n========================================\n'
    
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
    dice_message += Tm.block_quote(f' {Tm.inline_code("Total Dice Modifier")}: {Tm.bold_italics(total-temp_array[0])}\n>  \n')
    dice_message += Tm.block_quote(f' {Tm.inline_code("Modifier")}: {Tm.bold_italics(f"{modifier}{integer}")}')
    
    message += dice_message
    if(modifier == '-'):integer = integer*-1
    
    message += f'\n' + '> \n' + (f' {Tm.inline_code("Total")}: {Tm.bold_italics(f"{total+integer}")}\t')
    message += Tm.inline_code(f'Natural Roll Value') + f': {Tm.bold_italics(temp_array[0])}'
    await ctx.send(message)

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
        print(data)
        if data:
            print('yes')
            guilds.update(data)
        logger.info(f"(User: {bot.user}) (ID: {bot.user.id})")
        print("___________")
        
    @bot.command(
        aliases=['switchKarmic', 'sK', 'SK', 'Sk'],
        help="Entering this command will disable or Enable Karmic Dice for D20 rolls, !sk",
        description="Entering this command will disable or enable Karmic Dice, followed by a prompt determining which mode the bot is in.",
        brief="Switch whether dice are Karmic or Not."
    )
    async def sk(ctx):
        if karmic[0]:
            karmic[0] = False
        elif karmic[0] == False:
            karmic[0] = True
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
    
    @bot.command(
        aliases=["setName"],
        help="Set a custom name for the bot to use. !sn name",
        description="Allows a user to",
        brief="Brief Message"
    )
    async def sn(ctx, what):
        guild_id = str(ctx.guild.id)
        guild_id_hash = hash_string(guild_id)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        guilds.update({guild_id_hash: {user_id_hash: what} })
        exit_handler(ctx, guilds, guild_id_hash)
        await delete_message(ctx)
        await ctx.send(f'{ctx.author.name} set their Name to {guilds.get(guild_id_hash).get(user_id_hash)}')
    
    #Roll Command
    @bot.command(
        aliases=["roll", "R"],
        help="Roll's the specified dice with a potential modifier, !r 2d20 + 5",
        description="Rolls the said die, if no number precedes the die side, d20, it will assume there is only one.\n"+
        "Likewise, you may modifiy your roll by other dices by following the syntax: !r d20-2d4+4d6 + modifier\n" +
        "It only supports one numeric modifier that is not a die, and must be formatted as shown with a space on both sides of the arithmetic operator.",
        brief="Roll dice, modify your main dice roll and add a modifier."
    )
    async def r(ctx, what="No Dice were clarified", modifier="+", integer="0"):
        """Answers with pong"""
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        array = []
        if(integer.isdigit() == False):
            integer = 0
        if("d" in what):
            dice, operators = await process_roll(ctx, author, what)
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            logger.info(result['value'])
            logger.info(operators)
            await delete_message(ctx)
            await display_roll(ctx, what, result['value'], operators, modifier, int(integer))
                
            
    #Roll with Advantage
    @bot.command(
        aliases=["RA", "rollAdvantage", "rAdv", "rad", "rAd", "radv"],
        help="The same as the !roll command, except it will roll the first dice type with advantage. !ra d20+4 + 1",
        description="Syntax is the same as the !roll command, however it will roll the first die specified twice\ntaking the higher of the two results.",
        brief="Rolls the dice with advantage,and can be modified with other dice ......"
    )
    async def ra(ctx, what="No Dice were clarified", modifier="+", integer="0"):
        """Answers with pong"""
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        array = []
        if(integer.isdigit() == False):
            integer = 0
        if("d" in what):
            dice, operators = await process_roll(ctx, author, what)
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            result1 = result['value'][0]
            result2 = roll_dice(user_id_hash, dice[0])
            if sum(result1) > sum(result2):
                result['value'][0] = result1
            elif sum(result1) < sum(result2) or sum(result1) == sum(result2):
                result['value'][0] = result2
            logger.info(result['value'])
            await delete_message(ctx)
            await display_roll(ctx, what, result['value'], operators, modifier, int(integer), adv=True, rolls_array=[result1, result2])
    
    #Roll with Disadvantage
    @bot.command(
        aliases=["Rd","rollDisadvantage", "rDis", "rdis", "rDs", "rds"],
        help="Same as the !roll command except rolls first die with disadvantage. !rd d20 - 5",
        description="Rolls the first die twice, and takes the lowest result. Can still be modified by adding additional dice and a modifier.",
        brief="Rolls the dice with disadvantage."
    )
    async def rd(ctx, what="No Dice were clarified", modifier="+", integer="0"):
        """Answers with pong"""
        set_random_seed()
        author = await get_name(ctx)
        user_id = str(ctx.author.id)
        user_id_hash = hash_string(user_id)
        
        result = {"value":[]}
        array = []
        if(integer.isdigit() == False):
            integer = 0
        if("d" in what):
            dice, operators = await process_roll(ctx, author, what)
            for die in dice:
                result['value'].append(roll_dice(user_id_hash, die))
            result1 = result['value'][0]
            result2 = roll_dice(user_id_hash, dice[0])
            
            if sum(result1) < sum(result2):
                result['value'][0] = result1
            elif sum(result1) > sum(result2) or sum(result1) == sum(result2):
                result['value'][0] = result2
            logger.info(result['value'])
            await delete_message(ctx)
            await display_roll(ctx, what, result['value'], operators, modifier, int(integer), dis=True, rolls_array=[result1, result2])
    
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

    bot.run(settings.DISCORD_API_TOKEN, root_logger=True)
    
    print(settings.DISCORD_API_TOKEN)

if __name__ == "__main__":
    run()