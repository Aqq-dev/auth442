import discord
from discord.ext import commands
from discord import app_commands, Embed, ButtonStyle
from discord.ui import View, Button
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.tree.command(name="verify")
async def verify(interaction: discord.Interaction):
    embed = Embed(
        title="✅ アカウント認証",
        description="下のボタンを押して認証を行ってください。\nVPN・サブ垢の使用は禁止されています。",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Double Counter 風 認証システム")

    button = Button(
        label="認証を開始する",
        style=ButtonStyle.link,
        url=f"https://your-render-app.onrender.com/auth?user_id={interaction.user.id}"
    )

    view = View()
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)

bot.run(TOKEN)
