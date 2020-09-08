import discord
from discord.ext import commands
from discord.ext.commands import command
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
from discord import Client
import asyncio
import ast
import time
from collections.abc import Sequence
import praw
from praw import Reddit

# reading token from file
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

Client.fetch_user

# defining stuff
token = read_token()
client = commands.Bot(command_prefix='r/')
client.config_token = read_token()
client.remove_command('help')
ownerId = "176446054823100420"


# stuff that occurs on connecting
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="r/help", url="https://twitch.tv/jayjay8182"))
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

reddit = praw.Reddit(client_id = 'gdzJMO43TXWAMA',
                     client_secret = 'mOoE4bNoJd1A7xJ6zTcWO_b40JY',
                     username = 'MeGustaChungus',
                     password = 'BigChungus',
                     user_agent = 'DiscBot')

@client.command(pass_context = True)
async def top(ctx, arg):
    subreddit = reddit.subreddit(arg)

    top_subreddit = subreddit.top(limit=100)
    topPosts = []
    postTitles = []
    count = 0

    for submission in top_subreddit:
        if not submission.stickied:
            topPosts.append(submission.url)
            postTitles.append(submission.title)

    reacted_message = await ctx.send("**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])

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
                if count == (len(topPosts)):
                    count = 0
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])
            elif reaction.emoji == '⬅️':
                count -= 1
                if count == -1:
                    count = (len(topPosts)-1)
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])
            elif reaction.emoji == '⏩':
                count = (len(topPosts)-1)
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])
            elif reaction.emoji == '⏪':
                count = 0
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])
            elif reaction.emoji == '🔀':
                count = random.randint(0, len(topPosts))            
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count])
            elif reaction.emoji == '❌':
                react_cross = True
                await discord.Message.delete(reacted_message)

        except TimeoutError:
                await discord.Message.edit(reacted_message, content ="**Top posts in "+str(arg)+"**\npost `"+str(count+1)+'/'+str(len(topPosts))+"`\n> "+(postTitles[count])+'\n'+topPosts[count]+"\n Timed out")
    


# img command, uses web scraping to store images in a list and allows the user to scroll through them by adding reactions
@client.command(pass_context = True)
async def img(ctx, *args):
    term = (" ".join(args))
    url = "https://www.bing.com/images/search?q="+term+"&form=HDRSC2&safeSearch=off&mkt=en-US"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"
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
            'Client': Client,
            '__import__': __import__
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
    with open('commands.txt', 'r') as file:
        commands = file.read()
        commandsEmbed = discord.Embed(color=0x7A6C6C)
        commandsEmbed.add_field(name="Commands", value=commands, inline=False)
        commandsEmbed.set_thumbnail(url=(client.user.avatar_url))
        await ctx.channel.send(embed=commandsEmbed)


client.run(client.config_token)
