import discord
from discord.ext import commands
from discord.ext.commands import command
from datetime import datetime
import random
import requests
import itertools
from bs4 import BeautifulSoup
from discord import Client
import asyncio
import ast
import time
from collections.abc import Sequence
import praw
from yahoofinancials import YahooFinancials

# reading token from file
def read_token():
    with open(r"", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

# defining stuff
token = read_token()
client = commands.Bot(command_prefix='r/')
client.config_token = read_token()
client.remove_command('help')
ownerId = ""


# stuff that occurs on connecting
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="r/help", url=""))
    print("bot connected")

# scrolling embed functions
def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)

def reaction_check(message=None, emoji=None, author=None, ignore_bot=True):
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)
    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check

# bot commands
# mimic command, copys the users input and deletes the command message
@client.command(pass_context=True)
async def mimic(ctx, *args):
    mimicMessage = (" ".join(args))
    if '@everyone' in mimicMessage or '@here' in mimicMessage:
        await ctx.send("No pinging everyone")
    else:
        await ctx.message.delete()
        await ctx.send(" ".join(args))

# blackjack command =============================================================================================================
@client.command(pass_context=True)
async def blackjack(ctx):
    global vals, suits, deck, playerHand, playerScore, dealerHand, dealerScore, check, blackjack_Msg, blackjackEmbed
    
    vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']
    suits = ['spades', 'clubs', 'hearts', 'diamonds']
    playerHand = []
    playerScore = 0
    
    stand = False

    dealerHand = []
    dealerScore = 0
    
    deck = list(itertools.product(vals, suits))
    random.shuffle(deck)
    
    drawCard()
    drawCard()

    dealerHit()
    blackjackEmbed = discord.Embed(title="BlackJack", description=("Dealer's hand is " + str((dealerHand[0])[0]) + " of " + str((dealerHand[0])[1]) + " `score: " + str(dealerScore) + "`"
                                                                    + "\nYour hand is " + str((playerHand[0])[0]) + " of " + str((playerHand[0])[1])
                                                                    + " and " + str((playerHand[1])[0]) + " of " + str((playerHand[1])[1]) + " `score: " + str(playerScore)) + "`",
                                                                    timestamp=datetime.utcnow(), color=0x7A6C6C)
    blackjack_Msg = await ctx.channel.send(embed=blackjackEmbed)
    await discord.Message.add_reaction(blackjack_Msg, emoji="✅")
    await discord.Message.add_reaction(blackjack_Msg, emoji="🛑")

    while not stand:
        check = reaction_check(message=blackjack_Msg, author=ctx.author, emoji=('✅️', '🛑'))
        print(str(check))
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=90.0, check=check)
            print("hi")
            if reaction.emoji == '✅️':
                drawCard()
                blackjackEmbed = discord.Embed(title="Blackjack",  description=("Dealer's hand is " + str(dealerHand) + "\nYour hand is" + str(playerHand)) , timestamp=datetime.utcnow(), color=0x7A6C6C)
                await discord.Message.edit(blackjack_Msg, embed=blackjackEmbed)
            elif reaction.emoji == '🛑':
                stand = True
                break
        except TimeoutError:
            return

def bust():
    global playerHand, playerScore
    print(playerHand)
    print(playerScore)
    print("bust")

def dealerWin():
    global dealerHand, dealerScore
    print(dealerHand)
    print(dealerScore)
    print("bust")

def tie():
    print("draw")

def playerWin():
    print("you won")

def dealerTurn():
    global dealerHand, dealerScore, playerScore

    while dealerScore < playerScore and dealerScore < 22 or dealerScore == playerScore and dealerScore < 22:
        dealerHit()
        print("dealer hit")

        if dealerScore > playerScore and dealerScore < 22:
            dealerWin()
            break
        elif dealerScore > 21 and playerScore > 21:
            tie()
            break
        elif dealerScore == 21 and playerScore == 21:
            tie()
            break

    if dealerScore > 21:
        dealerBust()

    if dealerScore == 21 and playerScore == 21:
        tie()

    else:
        dealerWin()


def dealerBust():
    global playerscore, dealerScore, dealerHand

    if playerScore == dealerScore:
        tie()
    else:
        print("dealer bust")
        print(dealerHand, dealerScore)
        playerWin()

def full21(player):
    global playerHand, playerScore, dealerHand, dealerScore
    if player == "player":
        print("BlackJack!")
    elif player == "dealer":
        print("Dealer Blackjack")
        if playerScore == dealerScore:
            tie()
        else:
            dealerWin()

def drawCard():
    global playerScore
    card = random.choice(deck)
    playerHand.append(card)

    if card[0] == "ace":
        if (playerScore + 11) < 22:
            playerScore += 11

        else:
            playerScore += 1

    elif (type(card[0]) is str):
        if (playerScore + 10) > 21:
            playerScore += 10
            bust()
        else:
            playerScore += 10

    else:
        if (playerScore + int(card[0])) > 21:
            playerScore += int(card[0])
            bust()

        else:
            playerScore += int(card[0])

    if playerScore == 21:
        full21("player")

def dealerHit():
    global dealerScore, dealerHand
    card = random.choice(deck)
    dealerHand.append(card)

    if card[0] == "ace":
        if (dealerScore + 11) < 22:
            dealerScore += 11

        else:
            dealerScore += 1

    elif (type(card[0]) is str):
        dealerScore += 10

    else:
        dealerScore += int(card[0])

    if dealerScore == 21:
        full21("dealer")
    
    

# img command, uses web scraping to store images in a list and allows the user to scroll through them by adding reactions
@client.command(pass_context = True)
async def img(ctx, *args):
    term = (" ".join(args))
    url = 'https://bing.com/images/search?q=' + term + '&safeSearch=off' + "&FORM=HDRSC2" + '&count=100' + '&mkt=en-US' + '&adlt_set=off'
    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    headers = {"user-agent": USER_AGENT}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    count = 0
    linkList = []
    results = soup.find_all('a',class_='iusc')

    for i in results:
        linkList.append(eval(i['m'])['murl'])

    imgEmbed = discord.Embed(title="Image results for "+str(term), description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'), timestamp=datetime.utcnow(), color=0x7A6C6C)
    imgEmbed.set_image(url=linkList[count])
    reacted_message = await ctx.channel.send(embed=imgEmbed)

    await discord.Message.add_reaction(reacted_message, emoji="⏪")
    await discord.Message.add_reaction(reacted_message, emoji="⬅️")
    await discord.Message.add_reaction(reacted_message, emoji="➡️")
    await discord.Message.add_reaction(reacted_message, emoji="⏩")
    await discord.Message.add_reaction(reacted_message, emoji="🔀")
    await discord.Message.add_reaction(reacted_message, emoji="❌")

    react_cross = False
    while not react_cross:
        check = reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
        try: 
            reaction, user = await client.wait_for('reaction_add', timeout=90.0, check=check)
            if reaction.emoji == '➡️':
                count += 1
                if count == (len(linkList)):
                    count = 0
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                imgEmbed.set_image(url=linkList[count])
                await discord.Message.edit(reacted_message, embed=imgEmbed)
            elif reaction.emoji == '⬅️':    
                count -= 1
                if count == -1:
                    count = (len(linkList)-1)
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                imgEmbed.set_image(url=linkList[count])
                await discord.Message.edit(reacted_message, embed=imgEmbed)
            elif reaction.emoji == '⏪':
                count = 0
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                imgEmbed.set_image(url=linkList[count])
                await discord.Message.edit(reacted_message, embed=imgEmbed)
            elif reaction.emoji == '⏩':
                count = (len(linkList)-1)
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                imgEmbed.set_image(url=linkList[count])
                await discord.Message.edit(reacted_message, embed=imgEmbed)
            elif reaction.emoji == '🔀':
                count = random.randint(0, len(linkList))
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('img `'+str(count+1)+'/'+str(len(linkList))+'`'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                imgEmbed.set_image(url=linkList[count])
                await discord.Message.edit(reacted_message, embed=imgEmbed)
            elif reaction.emoji == '❌':
                react_cross = True
                await discord.Message.delete(reacted_message)

        except TimeoutError:
                imgEmbed = discord.Embed(title="Image results for "+str(term),  description=('Timed Out'),timestamp=datetime.utcnow(), color=0x7A6C6C)
                await discord.Message.edit(reacted_message, embed=imgEmbed)

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

# command that runs python code in code blocks and sends the output
@client.command()
async def run(ctx, *, cmd):
    if str(ctx.message.author.id) == ownerId:
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'time': time,
            'client': client,
            '__import__': __import__,
            'reddit': reddit
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        await ctx.send(result)
    else:
        await ctx.send("This command is reserved for the owner")


# dice roll command that takes a range from the user
@client.command()
async def roll(ctx, lValue, hValue):
    roll = random.randint(int(lValue), int(hValue))
    await ctx.send("you rolled `"+ str(roll)+ "`")


# server information command that displays key statistics about the server the user is in
@client.command()
async def serverinfo(ctx):
    member_count = len(ctx.guild.members)

    serverInfoEmbed = discord.Embed(title=" Server Stats for "+str(ctx.guild), timestamp=datetime.utcnow(), color=0x7A6C6C)
    serverInfoEmbed.set_thumbnail(url=ctx.guild.icon_url)

    fields = [("ID", ctx.guild.id, True),
                        ("Owner", "\@"+str(ctx.guild.owner), True),
                        ("Region", ctx.guild.region, True),
                        ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                        ("Text channels", len(ctx.guild.text_channels), True),
                        ("Voice channels", len(ctx.guild.voice_channels), True),
                        ("Members", str(member_count), True),
                        ("Boosts", str(ctx.guild.premium_subscription_count), True), 
                        ("Roles", len(ctx.guild.roles), True)]

    for name, value, inline in fields:
        serverInfoEmbed.add_field(name=name, value=value, inline=inline)
    await ctx.channel.send(embed=serverInfoEmbed)

# help command which sends the list of commands
@client.command()
async def help(ctx):
    with open(r"/home/pi/Downloads/Discord.py-Bot/commands.txt", 'r') as file:
        commands = file.read()
        commandsEmbed = discord.Embed(color=0x7A6C6C)
        commandsEmbed.add_field(name="Commands", value=commands, inline=False)
        commandsEmbed.set_thumbnail(url=(client.user.avatar_url))
        await ctx.channel.send(embed=commandsEmbed)

# sudo command to mimic user using a webhook
@client.command()
async def sudo(ctx, user, *message):

    user_to_copy = ctx.author

    if ctx.message.mentions:
        user_to_copy = ctx.message.mentions[0]
    else:
        for member in ctx.guild.members:
            if member.id == user or client.get_user(member.id).name == user or member.display_name == user:
                user_to_copy = member
                break

    sudoText = " ".join(message)
    await ctx.message.delete()
    webhook = await ctx.channel.create_webhook(name=user_to_copy.display_name)
    await webhook.send(content=sudoText, avatar_url=user_to_copy.avatar_url)
    await webhook.delete()
    
# shows the bots ping
@client.command()
async def ping(ctx):
    await ctx.send("`"+str(int(client.latency*1000))+"`ms")
    
#======================================== Reddit Commands ========================================#
with open(r"/home/pi/Downloads/Discord.py-Bot/token.txt", "r") as f:
        lines = f.readlines()
        
reddit = praw.Reddit(client_id = lines[2].strip(),
                     client_secret = lines[3].strip(),
                     username = lines[4].strip(),
                     password = lines[5].strip(),
                     user_agent = lines[6].strip())

# returns 100 reddit posts for the subname, popularity and timeframe
@client.command(pass_context = True)
async def sub(ctx, subName, type="top", timeframe="all"):
    sub = reddit.subreddit(subName)
    timeFilter = "all"
    filter = "top"
    subreddit_category_posts = sub.top("all", limit=100)

    if str(timeframe).lower() == "hour":
        timeFilter = "hour"
    elif str(timeframe).lower() == "day":
        timeFilter = "day"
    elif str(timeframe).lower() == "week":
        timeFilter = "week"
    elif str(timeframe).lower() == "month":
        timeFilter = "month"
    elif str(timeframe).lower() == "all":
        timeFilter = "all"

    if str(type).lower() == "top":
        subreddit_category_posts = sub.top(timeFilter, limit=100)
        filter = "Top"
    elif str(type).lower() == "hot":
        subreddit_category_posts = sub.hot(limit=100)
        filter = "Hot"
    elif str(type).lower() == "new":
        timeFilter = "all"
        subreddit_category_posts = sub.new(limit=100)
        filter = "New"
    elif str(type).lower() == "controversial":
        subreddit_category_posts = sub.controversial(timeFilter, limit=100)
        filter = "Controversial"


    Posts = []
    postTitles = []
    count = 0

    for submission in subreddit_category_posts:
        if not submission.stickied:
            Posts.append(submission.url)
            postTitles.append(submission.title)

    reacted_message = await ctx.send("**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])

    await discord.Message.add_reaction(reacted_message, emoji="⏪")
    await discord.Message.add_reaction(reacted_message, emoji="⬅️")
    await discord.Message.add_reaction(reacted_message, emoji="➡️")
    await discord.Message.add_reaction(reacted_message, emoji="⏩")
    await discord.Message.add_reaction(reacted_message, emoji="🔀")
    await discord.Message.add_reaction(reacted_message, emoji="❌")


    react_cross = False
    while not react_cross:
        check = reaction_check(message=reacted_message, author=ctx.author, emoji=('➡️', '⬅️', '⏪', '⏩', '🔀', '❌'))
        try: 
            reaction, user = await client.wait_for('reaction_add', timeout=90.0, check=check)
            if reaction.emoji == '➡️':
                count += 1
                if count == (len(Posts)):
                    count = 0
                await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])
            elif reaction.emoji == '⬅️':
                count -= 1
                if count == -1:
                    count = (len(Posts)-1)
                await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])
            elif reaction.emoji == '⏩':
                count = (len(Posts)-1)
                await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])
            elif reaction.emoji == '⏪':
                count = 0
                await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])
            elif reaction.emoji == '🔀':
                count = random.randint(0, len(Posts))
                await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count])
            elif reaction.emoji == '❌':
                react_cross = True
                await discord.Message.delete(reacted_message)

        except TimeoutError:
            await discord.Message.edit(reacted_message, content ="**"+filter + " posts in " + str(subName) + "**\n**Timeframe: " + timeFilter +"**\npost `" + str(count + 1) + '/' + str(len(Posts)) + "`\n> " + (postTitles[count]) + '\n' + Posts[count] + "\n**Timed Out")


@client.command(pass_context = True)
async def findsub(ctx, subName):
    subList = ""
    
    for subreddit in reddit.subreddits.search_by_name(str(subName)):
        subList += subreddit.display_name+"\n"
        
    if subList != "":
        await ctx.send("Subreddits matching: `"+subName+"` ```"+ subList+ "```")
    else:
        await ctx.send("No subs found")

#======================================== Crypto Commands ========================================#
@client.command()
async def stocks(ctx, stock):
    data = YahooFinancials(stock)
    if str(data.get_current_price()) != "None":
        await ctx.send("**"+stock.upper()+"-USD**"+"\n Current Value: `"+str(data.get_current_price())+"`\n " + "Daily Low/High: `"
         + str(data.get_daily_low()) + "`/`" + str(data.get_daily_high())+"`" + "\n Yearly Low/High: `" + str(data.get_yearly_low()) + "`/`" + str(data.get_yearly_high())+ "`") 
    else:
        await ctx.send("Invalid Listing")
        
@client.command()
async def crypto(ctx, coin):
    data = YahooFinancials(coin+"-usd")
    if str(data.get_current_price()) != "None":
        await ctx.send("**"+coin.upper()+"-USD**"+"\n Current Value: `"+str(data.get_current_price())+"`\n " + "Daily Low/High: `"
         + str(data.get_daily_low()) + "`/`" + str(data.get_daily_high())+"`" + "\n Yearly Low/High: `" + str(data.get_yearly_low()) + "`/`" + str(data.get_yearly_high())+ "`")
    else:
        await ctx.send("Invalid Listing")
        
#======================================== NSFW Commands ========================================#

Ass = ["Ass", "Booty", "Asstastic", "Bigasses", "twerking", "Pawg", "Asshole", "Whooties"]
Boobs = ["Boobs", "bigboobs", "stacked", "smallboobs", "hugeboobs", "boobies", "titties", "tittydrop", "massivetitsnass"] 
Pussy = ["upskirt", "pussy", "spreading", "godpussy", "rearpussy", "facedownassup"]
        
@client.command()
async def ass(ctx):
    posts = []
    for submission in reddit.subreddit(random.choice(Ass)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Ass from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        Embed = discord.Embed(title="Here's some Ass from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        Embed.set_image(url=post.url)
        await ctx.send(embed=Embed)      
    
@client.command()
async def boobs(ctx):
    posts = []
    for submission in reddit.subreddit(random.choice(Boobs)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Boobs from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        Embed = discord.Embed(title="Here's some Boobs from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        Embed.set_image(url=post.url)
        await ctx.send(embed=Embed)   
    
@client.command()
async def pussy(ctx):
    posts = []
    for submission in reddit.subreddit(random.choice(Pussy)).top(random.choice(("month", "year", "all")), limit=100):
        posts.append(submission)
    
    post = random.choice(posts)
    
    if "redgif" in post.url or "imgur" in post.url:
        await ctx.send("**Here's some Pussy from r/"+str(post.subreddit)+"**\n"+post.url)
    else:
        Embed = discord.Embed(title="Here's some Pussy from r/"+str(post.subreddit), timestamp=datetime.utcnow(), color=0x7A6C6C)
        Embed.set_image(url=post.url)
        await ctx.send(embed=Embed) 


client.run(client.config_token)
