import ssl
import certifi
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

ssl_context = ssl.create_default_context(cafile=certifi.where())
old_init = aiohttp.ClientSession.__init__

def new_init(self, *args, **kwargs):
    kwargs["connector"] = aiohttp.TCPConnector(ssl=ssl_context)
    old_init(self, *args, **kwargs)

aiohttp.ClientSession.__init__ = new_init

import django
import sys
import asyncio
import threading
from flask import Flask, request, jsonify
import discord
from discord.ext import commands
from asgiref.sync import sync_to_async

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'crypto.settings'
django.setup()

from users.models import User

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

@bot.event
async def on_ready():
    print(f"{bot.user} connected")
    print(f"ID: {bot.user.id}")

@bot.command(name="register")
async def register_command(ctx, email: str, password: str, first_name: str, last_name: str, country: str, phone: str):
    discord_id = str(ctx.author.id)
    try:
        exists = await sync_to_async(User.objects.filter(email=email).exists)()
        if exists:
            await ctx.send(f"{ctx.author.mention} Email already used")
            return
        phone_exists = await sync_to_async(User.objects.filter(phone=phone).exists)()
        if phone_exists:
            await ctx.send(f"{ctx.author.mention} Phone used")
            return
        disc_exists = await sync_to_async(User.objects.filter(discord_id=discord_id).exists)()
        if disc_exists:
            await ctx.send(f"{ctx.author.mention} Discord linked")
            return
        user = await sync_to_async(User.objects.create_user)(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            country=country,
            phone=phone,
            discord_id=discord_id
        )
        embed = discord.Embed(title="Registration Complete", color=discord.Color.green())
        embed.add_field(name="Email", value=email)
        embed.add_field(name="Country", value=country)
        embed.add.add_field(name="Phone", value=phone)
        embed.add_field(name="User ID", value=str(user.id))
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name="login")
async def login_command(ctx, email: str, password: str):
    discord_id = str(ctx.author.id)
    try:
        try:
            user = await sync_to_async(User.objects.get)(email=email)
        except:
            await ctx.send("User not found")
            return
        valid = await sync_to_async(user.check_password)(password)
        if not valid:
            await ctx.send("Invalid password")
            return
        if not user.is_active:
            await ctx.send("Account disabled")
            return
        if not user.discord_id:
            user.discord_id = discord_id
            await sync_to_async(user.save)()
        elif user.discord_id != discord_id:
            await ctx.send("Linked to another user")
            return
        embed = discord.Embed(title="Login Successful", color=discord.Color.blue())
        embed.add_field(name="Email", value=user.email)
        embed.add_field(name="2FA", value="Enabled" if user.two_factor_enabled else "Disabled")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.json
    discord_id = data["discord_id"]
    code = data["code"]
    email = data["email"]
    ip = data["ip"]
    location = data["location"]

    def sync_send():
        try:
            f = asyncio.run_coroutine_threadsafe(
                send_dm(discord_id, code, email, ip, location), bot.loop
            )
            return f.result(timeout=10)
        except:
            return False

    if sync_send():
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 500

async def send_dm(discord_id, code, email, ip, location):
    try:
        user = await bot.fetch_user(int(discord_id))
        embed = discord.Embed(title="2FA Code", color=discord.Color.gold())
        embed.add_field(name="Code", value=f"```{code}```")
        embed.add_field(name="Email", value=email)
        embed.add_field(name="IP", value=ip)
        embed.add_field(name="Location", value=location)
        await user.send(embed=embed)
        return True
    except:
        return False

@app.route("/send-password-reset", methods=["POST"])
def send_password_reset():
    data = request.json
    discord_id = data["discord_id"]
    code = data["code"]
    email = data["email"]
    ip = data["ip"]
    location = data["location"]

    def sync_send():
        try:
            f = asyncio.run_coroutine_threadsafe(
                send_reset(discord_id, code, email, ip, location), bot.loop
            )
            return f.result(timeout=10)
        except:
            return False

    if sync_send():
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 500

async def send_reset(discord_id, code, email, ip, location):
    try:
        user = await bot.fetch_user(int(discord_id))
        embed = discord.Embed(title="Password Reset", color=discord.Color.blue())
        embed.add_field(name="Reset Code", value=f"```{code}```")
        embed.add_field(name="Email", value=email)
        embed.add_field(name="IP", value=ip)
        embed.add_field(name="Location", value=location)
        await user.send(embed=embed)
        return True
    except:
        return False

def run_flask():
    app.run(host="0.0.0.0", port=5055)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.run(TOKEN)
