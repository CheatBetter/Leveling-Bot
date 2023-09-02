"""
Copyright 2023 CheatBetter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Join Us
"""
import discord
from discord.ext import commands
import sqlite3

bot = commands.Bot(command_prefix="!")

# Connect to SQLite database
conn = sqlite3.connect("levels.db")
cursor = conn.cursor()

# Create a table for user levels if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS levels (
        user_id INTEGER PRIMARY KEY,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0
    )
""")
conn.commit()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

        # Check if the user is in the database; if not, add them
    cursor.execute("SELECT * FROM levels WHERE user_id = ?", (message.author.id,))
    user_data = cursor.fetchone()
    if user_data is None:
        cursor.execute("INSERT INTO levels (user_id) VALUES (?)", (message.author.id,))
        conn.commit()
        user_data = (message.author.id, 1, 0)

    # Update user's XP and check for level up
    user_id, user_level, user_xp = user_data
    user_xp += calculate_xp(user_level)

    # Check for level up
    while user_xp >= calculate_xp(user_level + 1):
        user_xp -= calculate_xp(user_level + 1)
        user_level += 1
        await message.channel.send(f"{message.author.mention} leveled up to Level {user_level}!")

    cursor.execute("UPDATE levels SET level = ?, xp = ? WHERE user_id = ?", (user_level, user_xp, user_id))
    conn.commit()

    await bot.process_commands(message)


@bot.slash_command()
async def profile(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    # Fetch user's level and XP from the database
    cursor.execute("SELECT level, xp FROM levels WHERE user_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        level, xp = result
    else:
        level, xp = 1, 0

    # Create an embed to display the user's profile
    embed = discord.Embed(title=f"Profile for {user.name}", color=discord.Color.blue())
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=xp, inline=True)

    await ctx.send(embed=embed)


def calculate_xp(level):
    # Calculate the XP required for the next level (customizable)
    return 100 * level  # You can adjust this formula as needed


# Run the bot with your token
bot.run("MTE0NzM2ODE5NDc4MTIyOTA5Nw.Glm89U.ZxiE6_7t9YJhvdjtHcqXFtfxdh8gPb5-a_sOEA")
