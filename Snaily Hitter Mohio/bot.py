import discord
import hashlib
import asyncio
import requests
import json
from discord.ext import commands, tasks
from pymongo import MongoClient

client = MongoClient("")
db = client['mohiodb']
collection = db['users']

required_guild_id = 1179423799242936341
required_welcome_channel_id = 1179779795387678791
ticket_channel_id = 1179991838996832266
required_owner_role_id = 1179711628040736768
required_customer_role_id = 1179711581588828170

# snaily hitter logs
logs_create_account = ''
logs_delete_account = ''
logs_clearlogs = ''
logs_resetpassword = ''
logs_announcement = ''
# discord logs
logs_ban = ''

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)
client.allow_private_messages = True
client.remove_command("help")

@client.event
async def on_ready():
    print(f'Zalogowano jako {client.user.name} ({client.user.id})')
    await client.change_presence(activity=discord.Game(name="!help - #cmd"))

@client.event
async def on_member_join(member):
    channel = client.get_channel(required_welcome_channel_id)

    if channel is not None:
        await channel.send(f'**Welcome, {member.mention} to snaily hitter!**')

async def send_and_delete(ctx, content, delay=5):
    message = await ctx.send(content)
    await asyncio.sleep(delay)
    await message.delete()

@client.command(name='help')
async def command(ctx):
    target_channel = ctx.guild.get_channel(ticket_channel_id)
    embed = discord.Embed(title="", description="## Snaily Hitter - Commands (automatic delete 30sec)\n```-> [Everyone]\n• !price\n\n-> [Only Customer]\n• !decline\n• !getcreds\n• !clearlogs username\n• !resetpassword username fingerprint hashed_password\n\n-> [Only Admin] Snaily Hitter\n• !create username password fingerprint ip\n• !delete username\n• !announcement 'message'\n• !userinfo username\n\n-> [Only Admin] Discord\n• !ban username ```\n**Problem? contact: {}**".format(target_channel.mention), color=0x00ff00)

    if isinstance(ctx.channel, discord.DMChannel):
        message = await ctx.author.send(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    await ctx.message.delete()
    await asyncio.sleep(30)
    await message.delete()

@client.command(name='price')
async def price(ctx):
    target_channel = ctx.guild.get_channel(ticket_channel_id)
    embed = discord.Embed(title="", description="## Snaily Hitter - Price/Addons (automatic delete 30sec)\n```--Plan Role\n\n-> Lifetime\n• 80PLN | 20$\n\n-> Month\n• 50PLN |  12$\n\n-> Week\n• 30PLN | 8$\n\n--Payment Methods\n\n-> PaySafeCard + 15%\n-> PayPal + 0%\n-> BLIK + 0%\n-> Steam Items + 20%\n-> Crypto + 5%\n\n--Addons\n\n-> Premium 3 bin\n• 40PLN | 10$\n-> Proxy\n• SOON | SOON```\n**Buy: {}**".format(target_channel.mention), color=0x00ff00)

    if isinstance(ctx.channel, discord.DMChannel):
        message = await ctx.author.send(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    await ctx.message.delete()
    await asyncio.sleep(30)
    await message.delete()

@client.command(name='decline')
async def decline(ctx):
    embed = discord.Embed(title="", description="## Snaily Hitter - Decline means (automatic delete 30sec)\n```generic_decline - too many persons are hitting same site (try to use other email, and clear cookies)\n\nfraudulent - too many persons are hitting same site (try to use other email, and clear cookies)\n\ninvalid_account - card is invalid\n\ndo_not_honor - normal declinen\n\nincorrect_number - card is invalid\n\ntestmode_charges_only - card u used are invalid or the site from u want to buy enabled test mode\n\ninsufficient_funds - card is valid, but dont have money```", color=0x00ff00)

    required_rolecustomer = ctx.guild.get_role(required_customer_role_id)
    if required_rolecustomer is None:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
        return

    if required_rolecustomer not in ctx.author.roles:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
        return

    if isinstance(ctx.channel, discord.DMChannel):
        message = await ctx.author.send(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    await ctx.message.delete()
    await asyncio.sleep(30)
    await message.delete()

@client.command(name='getcreds')
async def decline(ctx):
    embed = discord.Embed(title="", description="## Snaily Hitter - Get Creds (automatic delete 30sec)\n**Connect to proxy:** https://snaily/getcreds", color=0x00ff00)

    required_rolecustomer = ctx.guild.get_role(required_customer_role_id)
    if required_rolecustomer is None:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
        return

    if required_rolecustomer not in ctx.author.roles:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
        return

    if isinstance(ctx.channel, discord.DMChannel):
        message = await ctx.author.send(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    await ctx.message.delete()
    await asyncio.sleep(30)
    await message.delete()
    

@client.command(name='create')
async def create_user(ctx, username=None, password=None, fingerprint=None, ip=None):
    try:
        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return


        if username is None or password is None or fingerprint is None or ip is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Enter all required arguments: username, password, fingerprint, ip"))
            return

        new_user = {
            "username": username,
            "password": hashlib.sha256(password.encode('utf-8')).hexdigest(),
            "fingerprint": fingerprint,
            "ip": ip,
            "settings": {
                "bin": "",
                "proxy": "",
                "logs": ["orange:orange:Welcome to 🐌 hitter!"]
            },
            "role": "customer",
            "invites": {}
        }

        result = collection.insert_one(new_user)

        # parsedkeydoc = {"_id": "some_id"}
        # paymentkeys = db['paymentkeys']
        # paymentkeys.update_one({"_id": parsedkeydoc["_id"]}, {"$set": {"is_used": True}})

        user = collection.find_one({"username": username})
        if user:
            # collection.update_one({"_id": user["_id"]}, {"$set": {"invites.{}.is_used".format(username): True}})
            # collection.update_one({"_id": user["_id"]}, {"$set": {"invites.{}.who_used".format(username): username}})
            collection.update_one({"_id": user["_id"]}, {"$set": {"invites.{}.create_by".format(username): ctx.author.name}})
            # collection.update_one({"_id": user["_id"]}, {"$set": {"invites.{}.invite_by".format(username): ctx.author.send}})
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"User {username} does not exist"))

        headers = {
					"Content-Type": "application/json"
				}
        embed_data = {
					"embeds": [
						{
							"description": "## Snaily Hitter - Logs Create",
							"color": 16776960,
							"fields": [
								{"name": "", "value": f"**Username: {username}**", "inline": True},
                                {"name": "", "value": f"**Password:** ||{password}||", "inline": False},
                                {"name": "", "value": f"**Fingerprint:** ||{fingerprint}||", "inline": False},
                                {"name": "", "value": f"**IP:** ||{ip}||", "inline": False},
                                {"name": "", "value": f"**Create by: {ctx.author.name}**", "inline": False},
							]
						}
					]
				}
        requests.post(logs_create_account, headers=headers, data=json.dumps(embed_data))

        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The new user {username} has been successfully created and saved to the database"))

    except Exception as e:
        print(f"Błąd podczas obsługi komendy create: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))

@client.command(name='announcement')
async def announcement(ctx, message=None):
    try:
        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return

        if message is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Please provide a message for the announcement"))
            return

        all_users = collection.find({})

        for user in all_users:
            if 'settings' in user and 'logs' in user['settings']:
                user['settings']['logs'].append(message)
                collection.update_one({"_id": user["_id"]}, {"$set": {"settings.logs": user['settings']['logs']}})

        headers = {
            "Content-Type": "application/json"
        }
        embed_data = {
            "embeds": [
                {
                    "description": "## Snaily Hitter - Announcement",
                    "color": 65280,
                    "fields": [
                        {"name": "", "value": f"**Announcement:** {message}", "inline": False},
                        {"name": "", "value": f"**Announced by: {ctx.author.name}**", "inline": False},
                    ]
                }
            ]
        }
        requests.post(logs_announcement, headers=headers, data=json.dumps(embed_data))

        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The announcement has been sent to all users"))
    except Exception as e:
        print(f"An error occurred while processing the announcement command: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))

@client.command(name='clearlogs')
async def clear_logs(ctx, username=None):
    try:
        required_customer_role = ctx.guild.get_role(required_customer_role_id)
        required_owner_role = ctx.guild.get_role(required_owner_role_id)

        if required_customer_role is None or required_owner_role is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_customer_role not in ctx.author.roles and required_owner_role not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return

        if username is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Enter your discord name"))
            return

        if required_owner_role not in ctx.author.roles and username != ctx.author.name:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "The username you entered does not match your discord name"))
            return

        user = collection.find_one({"username": username})
        if user:
            collection.update_one({"_id": user["_id"]}, {"$set": {"settings.logs": []}})
            
            collection.update_one({"_id": user["_id"]}, {"$push": {"settings.logs": "orange:orange:Welcome to 🐌 hitter!"}})
            
            headers = {
					"Content-Type": "application/json"
				}
            embed_data = {
					"embeds": [
						{
							"description": "## Snaily Hitter - Logs ClearLogs",
							"color": 16776960,
							"fields": [
								{"name": "", "value": f"**Username: {username}**", "inline": True},
                                {"name": "", "value": f"**ClearLogs By: {ctx.author.name}**", "inline": False},
							]
						}
					]
				}
            requests.post(logs_clearlogs, headers=headers, data=json.dumps(embed_data))

            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"You have successfully cleared your logs"))
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"You entered an incorrect discord nickname, your nickname {ctx.author.name}"))

    except Exception as e:
        print(f"Błąd podczas obsługi komendy clearlogs: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))



@client.command(name='delete')
async def delete_user(ctx, username=None):
    try:
        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command"))
            return

        if username is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Enter the username to delete"))
            return

        user = collection.find_one({"username": username})
        if user:

            headers = {
					"Content-Type": "application/json"
				}
            embed_data = {
					"embeds": [
						{
						    "description": "## Snaily Hitter - Logs Delete Account",
							"color": 16776960,
							"fields": [
								{"name": "", "value": f"**Username: {username}**", "inline": True},
                                {"name": "", "value": f"**Delete By: {ctx.author.name}**", "inline": False},
							]
						}
					]
				}
            requests.post(logs_delete_account, headers=headers, data=json.dumps(embed_data))

            collection.delete_one({"username": username})
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The user named {username} has been successfully deleted"))
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The user named {username} does not exist"))

    except Exception as e:
        print(f"Błąd podczas obsługi komendy delete: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx,"An error occurred while processing the command"))

@client.command(name='userinfo')
async def userinfo(ctx, username=None):
    try:

        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return
        
        user = collection.find_one({"username": username})
        if user:
            embed = discord.Embed(title="**Snaily Hitter - Userinfo (automatic delete 30sec)**", color=0x00ff00)
            embed.add_field(name="Username:", value=user.get('username', 'Brak'), inline=True)
            embed.add_field(name="Fingerprint:", value=user.get('fingerprint', 'Brak'), inline=True)
            embed.add_field(name="Create By:", value=user.get('invites', {}).get(username, {}).get('create_by', 'Brak'), inline=True)
            embed.add_field(name="<====================================================================>", value="", inline=False)
            embed.add_field(name="Bin:", value=user.get('settings', {}).get('bin', 'Brak'), inline=False)
            embed.add_field(name="Proxy:", value=user.get('settings', {}).get('proxy', 'Brak'), inline=False)

            message = await ctx.send(embed=embed)
            await ctx.message.delete()
            await asyncio.sleep(30)
            await message.delete()
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The user named {username} does not exist"))

    except Exception as e:
        print(f"Błąd podczas obsługi komendy userinfo: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))


@client.command(name='resetpassword')
async def resetpassword(ctx, username=None, new_fingerprint=None, new_password=None):
    try:
        required_customer_role = ctx.guild.get_role(required_customer_role_id)
        required_owner_role = ctx.guild.get_role(required_owner_role_id)

        if required_customer_role is None or required_owner_role is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_customer_role not in ctx.author.roles and required_owner_role not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return

        if username is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Enter your discord name"))
            return

        if required_owner_role not in ctx.author.roles and username != ctx.author.name:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "The username you entered does not match your discord name"))
            return

        user = collection.find_one({"username": username})
        if user:
            if new_fingerprint is not None:
                collection.update_one({"_id": user["_id"]}, {"$set": {"fingerprint": new_fingerprint}})

            if new_password is not None:
                collection.update_one({"_id": user["_id"]}, {"$set": {"password": hashlib.sha256(new_password.encode('utf-8')).hexdigest()}})

            headers = {
					"Content-Type": "application/json"
				}
            embed_data = {
					"embeds": [
						{
							"description": "## Snaily Hitter - Logs Resetpassword",
							"color": 16776960,
							"fields": [
								{"name": "", "value": f"**Username: {username}**", "inline": True},
                                {"name": "", "value": f"**Fingerprint:** ||{new_fingerprint}||", "inline": True},
                                {"name": "", "value": f"**Password:** ||{new_password}||", "inline": True},
                                {"name": "", "value": f"**Resetpassword By: {ctx.author.name}**", "inline": False},
							]
						}
					]
				}
            requests.post(logs_resetpassword, headers=headers, data=json.dumps(embed_data))

            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"Password reset successfully"))
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"The user named {username} does not exist you use {ctx.author.name}"))

    except Exception as e:
        print(f"Błąd podczas obsługi komendy update: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))

@client.command(name='ban')
async def ban_user(ctx, member: discord.Member = None, *, reason="No reason provided"):
    try:
        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return

        if member is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Please mention the user to ban"))
            return

        await ctx.message.delete()

        member_name = member.name
        member_id = member.id

        ban_message = f"You've been banned from {ctx.guild.name} by {ctx.author.name}. Reason: {reason}"
        await member.send(ban_message)

        await member.ban(reason=reason)

        headers = {
            "Content-Type": "application/json"
        }
        embed_data = {
            "embeds": [
                {
                    "description": "## Snaily Hitter - Logs Ban",
                    "color": 16776960,
                    "fields": [
                        {"name": "", "value": f"**Username: {member_name}**", "inline": True},
                        {"name": "", "value": f"**Reason:** ||{reason}||", "inline": True},
                        {"name": "", "value": f"**Banned By: {ctx.author.name}**", "inline": False},
                    ]
                }
            ]
        }
        requests.post(logs_ban, headers=headers, data=json.dumps(embed_data))

    except discord.Forbidden:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "I don't have permissions to ban this user"))
    except Exception as e:
        print(f"An error occurred while processing the ban command: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))

@client.command(name='unban')
async def unban_user(ctx, *, member_id=None):
    try:
        required_roleaccess = ctx.guild.get_role(required_owner_role_id)
        if required_roleaccess is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Configuration error: Required role not found"))
            return

        if required_roleaccess not in ctx.author.roles:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "You do not have the required role to execute this command."))
            return

        if member_id is None:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "Please provide the user ID to unban"))
            return

        banned_user = await ctx.guild.fetch_ban(discord.Object(id=int(member_id)))
        if banned_user:
            await ctx.guild.unban(banned_user.user)
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"User with ID `{member_id}` has been unbanned"))
        else:
            await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, f"User with ID `{member_id}` is not currently banned"))

    except discord.Forbidden:
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "I don't have permissions to unban this user"))
    except Exception as e:
        print(f"An error occurred while processing the unban command: {e}")
        await asyncio.gather(ctx.message.delete(), send_and_delete(ctx, "An error occurred while processing the command"))





client.run('')
