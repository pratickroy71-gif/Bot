import discord
from discord.ext import commands
import os
from openai import OpenAI

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

user_memory = {}

def get_ai_reply(user_id, username, message):
    if user_id not in user_memory:
        user_memory[user_id] = []
    
    user_memory[user_id].append({"role": "user", "content": message})
    
    messages = [
        {
            "role": "system",
            "content": f"Tum Foxy naam ka ek friendly, funny, helpful Discord bot ho. Tum hamesha Hindi me reply karte ho. User ka naam {username} hai."
        }
    ] + user_memory[user_id][-10:]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200
        )
        
        reply = response.choices[0].message.content
        
        user_memory[user_id].append({"role": "assistant", "content": reply})
        
        return reply
    
    except Exception as e:
        print("OpenAI Error:", e)
        return "⚠️ Maaf kijiye, abhi AI available nahi hai."

@bot.event
async def on_ready():
    print(f"✅ Ultimate Foxy v3 Online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    reply = get_ai_reply(
        str(message.author.id),
        message.author.name,
        message.content
    )
    
    await message.reply(reply)
    await bot.process_commands(message)

@bot.tree.command(name="ai", description="Foxy AI se baat kare")
async def ai(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    reply = get_ai_reply(
        str(interaction.user.id),
        interaction.user.name,
        question
    )
    
    await interaction.followup.send(reply)

@bot.tree.command(name="reset", description="Memory reset kare")
async def reset(interaction: discord.Interaction):
    user_memory[str(interaction.user.id)] = []
    await interaction.response.send_message("✅ Memory reset ho gayi.")

bot.run(DISCORD_TOKEN)
