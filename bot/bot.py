import django
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'crypto.settings'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

django.setup()

import discord
from discord.ext import commands
from flask import Flask, request, jsonify
from asgiref.sync import sync_to_async
import threading
import asyncio

from users.models import User

print("=" * 50)
print("User model fields:")
print([f.name for f in User._meta.get_fields()])
print("=" * 50)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)

TOKEN = ''


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('Bot is ready to accept commands!')


@bot.command(name='register')
async def register_user(ctx, email: str, password: str, first_name: str, last_name: str, country: str, phone: str):
    discord_id = str(ctx.author.id)

    try:
        email_exists = await sync_to_async(User.objects.filter(email=email).exists)()
        if email_exists:
            await ctx.send(f'{ctx.author.mention} User with this email already exists!')
            return

        phone_exists = await sync_to_async(User.objects.filter(phone=phone).exists)()
        if phone_exists:
            await ctx.send(f'{ctx.author.mention} User with this phone already exists!')
            return

        discord_exists = await sync_to_async(User.objects.filter(discord_id=discord_id).exists)()
        if discord_exists:
            await ctx.send(f'{ctx.author.mention} Your Discord account is already linked to another user!')
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

        embed = discord.Embed(
            title='Registration Successful',
            description=f'Welcome {first_name} {last_name}!',
            color=discord.Color.green()
        )
        embed.add_field(name='Email', value=email, inline=False)
        embed.add_field(name='Phone', value=phone, inline=False)
        embed.add_field(name='Country', value=country, inline=False)
        embed.add_field(name='User ID', value=str(user.id), inline=False)
        embed.set_footer(text='Use !login to sign in or !enable2fa to enable two-factor authentication')

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Registration failed: {str(e)}')


@bot.command(name='login')
async def login_user(ctx, email: str, password: str):
    discord_id = str(ctx.author.id)

    try:
        try:
            user = await sync_to_async(User.objects.get)(email=email)
        except User.DoesNotExist:
            await ctx.send(f'{ctx.author.mention} User not found!')
            return

        password_valid = await sync_to_async(user.check_password)(password)
        if not password_valid:
            await ctx.send(f'{ctx.author.mention} Invalid credentials!')
            return

        if not user.is_active:
            await ctx.send(f'{ctx.author.mention} Your account is disabled!')
            return

        if not user.discord_id:
            user.discord_id = discord_id
            await sync_to_async(user.save)()
        elif user.discord_id != discord_id:
            await ctx.send(f'{ctx.author.mention} This account is linked to another Discord user!')
            return

        embed = discord.Embed(
            title='Login Successful',
            description=f'Welcome back {user.first_name}!',
            color=discord.Color.blue()
        )
        embed.add_field(name='Email', value=user.email, inline=False)
        embed.add_field(name='2FA Status', value='Enabled' if user.two_factor_enabled else 'Disabled', inline=False)
        embed.set_footer(text='Use !enable2fa or !disable2fa to manage two-factor authentication')

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Login failed: {str(e)}')


@bot.command(name='enable2fa')
async def enable_2fa(ctx):
    discord_id = str(ctx.author.id)

    try:
        try:
            user = await sync_to_async(User.objects.get)(discord_id=discord_id)
        except User.DoesNotExist:
            await ctx.send(f'{ctx.author.mention} You need to register or login first!')
            return

        if user.two_factor_enabled:
            await ctx.send(f'{ctx.author.mention} Two-factor authentication is already enabled!')
            return

        user.two_factor_enabled = True
        await sync_to_async(user.save)()

        embed = discord.Embed(
            title='2FA Enabled',
            description='Two-factor authentication has been enabled for your account.',
            color=discord.Color.green()
        )
        embed.add_field(
            name='How it works',
            value='When you log in from the website, you will receive a verification code in Discord.',
            inline=False
        )
        embed.set_footer(text='Use !disable2fa to disable two-factor authentication')

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Error: {str(e)}')


@bot.command(name='disable2fa')
async def disable_2fa(ctx):
    discord_id = str(ctx.author.id)

    try:
        try:
            user = await sync_to_async(User.objects.get)(discord_id=discord_id)
        except User.DoesNotExist:
            await ctx.send(f'{ctx.author.mention} You need to register or login first!')
            return

        if not user.two_factor_enabled:
            await ctx.send(f'{ctx.author.mention} Two-factor authentication is already disabled!')
            return

        user.two_factor_enabled = False
        await sync_to_async(user.save)()

        embed = discord.Embed(
            title='2FA Disabled',
            description='Two-factor authentication has been disabled for your account.',
            color=discord.Color.orange()
        )
        embed.set_footer(text='Use !enable2fa to enable two-factor authentication')

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Error: {str(e)}')


@bot.command(name='profile')
async def show_profile(ctx):
    discord_id = str(ctx.author.id)

    try:
        try:
            user = await sync_to_async(User.objects.get)(discord_id=discord_id)
        except User.DoesNotExist:
            await ctx.send(f'{ctx.author.mention} You need to register or login first!')
            return

        embed = discord.Embed(
            title='Your Profile',
            color=discord.Color.blue()
        )
        embed.add_field(name='Name', value=f'{user.first_name} {user.last_name}', inline=False)
        embed.add_field(name='Email', value=user.email, inline=False)
        embed.add_field(name='Phone', value=user.phone, inline=False)
        embed.add_field(name='Country', value=user.country, inline=False)
        embed.add_field(name='User ID', value=str(user.id), inline=False)
        embed.add_field(name='2FA Status', value='Enabled' if user.two_factor_enabled else 'Disabled', inline=False)
        embed.set_footer(text=f'Account created: {user.created_at.strftime("%Y-%m-%d %H:%M")}')

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Error: {str(e)}')


@bot.command(name='help_auth')
async def help_command(ctx):
    embed = discord.Embed(
        title='Authentication Bot Commands',
        description='Here are all available commands:',
        color=discord.Color.purple()
    )

    embed.add_field(
        name='!register <email> <password> <first_name> <last_name> <country> <phone>',
        value='Register a new account',
        inline=False
    )
    embed.add_field(
        name='!login <email> <password>',
        value='Login to your account',
        inline=False
    )
    embed.add_field(
        name='!enable2fa',
        value='Enable two-factor authentication',
        inline=False
    )
    embed.add_field(
        name='!disable2fa',
        value='Disable two-factor authentication',
        inline=False
    )
    embed.add_field(
        name='!profile',
        value='View your profile information',
        inline=False
    )
    embed.add_field(
        name='!unlink',
        value='Unlink Discord account from your user account',
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(name='unlink')
async def unlink_discord(ctx):
    discord_id = str(ctx.author.id)

    try:
        try:
            user = await sync_to_async(User.objects.get)(discord_id=discord_id)
        except User.DoesNotExist:
            await ctx.send(f'{ctx.author.mention} Your Discord account is not linked to any user!')
            return

        user.discord_id = None
        user.two_factor_enabled = False
        await sync_to_async(user.save)()

        embed = discord.Embed(
            title='Discord Unlinked',
            description='Your Discord account has been unlinked.',
            color=discord.Color.orange()
        )
        embed.add_field(
            name='Important',
            value='Two-factor authentication has been disabled.',
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'{ctx.author.mention} Error: {str(e)}')


@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    discord_id = data.get('discord_id')
    code = data.get('code')
    ip = data.get('ip')
    location = data.get('location')
    email = data.get('email')

    def send_dm_sync():
        try:
            future = asyncio.run_coroutine_threadsafe(send_dm_async(discord_id, code, email, ip, location), bot.loop)
            result = future.result(timeout=10)
            return result
        except Exception as e:
            print(f'Error in send_dm_sync: {e}')
            return False

    result = send_dm_sync()

    if result:
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Failed to send DM'}), 500


async def send_dm_async(discord_id, code, email, ip, location):
    try:
        user = await bot.fetch_user(int(discord_id))

        embed = discord.Embed(
            title='Login Verification Code',
            description='Someone is trying to log into your account.',
            color=discord.Color.gold()
        )
        embed.add_field(name='Verification Code', value=f'```{code}```', inline=False)
        embed.add_field(name='Email', value=email, inline=False)
        embed.add_field(name='IP Address', value=ip, inline=True)
        embed.add_field(name='Location', value=location, inline=True)
        embed.add_field(
            name='Important',
            value='This code expires in 5 minutes.',
            inline=False
        )
        embed.set_footer(text='Never share this code with anyone')

        await user.send(embed=embed)
        print(f'2FA code sent successfully to user {discord_id}')
        return True
    except discord.errors.Forbidden:
        print(f'Cannot send DM to user {discord_id} - DMs are disabled')
        return False
    except Exception as e:
        print(f'Error sending DM: {e}')
        return False


def run_flask():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print('Starting Discord bot...')
    print('Flask API running on http://localhost:5000')
    bot.run(TOKEN)
