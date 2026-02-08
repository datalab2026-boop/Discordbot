import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from flask import Flask
from threading import Thread

# --- ВЕБ-СЕРВЕР ДЛЯ KOYEB (чтобы бот не отключался) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run():
    # Koyeb выдает порт автоматически через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ЛОГИКА УРОВНЕЙ ---
DATA_FILE = "server_levels.json"
MAX_LEVEL = 12

EXP_THRESHOLDS = {
    0: 0, 1: 100, 2: 500, 3: 2000, 4: 4500, 5: 8000, 
    6: 12500, 7: 18000, 8: 24500, 9: 32000, 
    10: 40500, 11: 50000, 12: 60500
}

active_boards = {} 

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_stats(data, guild_id):
    gid = str(guild_id)
    if gid not in data:
        data[gid] = {"level": 0, "current": 0}
    return data[gid]

def sync_level(exp):
    lvl = 0
    for l, val in EXP_THRESHOLDS.items():
        if exp >= val: lvl = l
        else: break
    return lvl

def create_embed(stats, guild_name):
    lvl, curr = stats["level"], stats["current"]
    embed = discord.Embed(title=f"📊 Server Progress: {guild_name}", color=0x3498DB)
    
    if lvl >= MAX_LEVEL:
        bar = "🟦" * 15
        embed.add_field(name=f"Level {lvl} (MAX)", value=f"{bar} **100%**", inline=False)
        embed.add_field(name="Total Experience", value=f"💎 `{curr:,}`", inline=True)
    else:
        start, end = EXP_THRESHOLDS[lvl], EXP_THRESHOLDS[lvl+1]
        progress = min(max((curr - start) / (end - start), 0), 1.0)
        bar = "🟦" * int(progress * 15) + "⬜" * (15 - int(progress * 15))
        embed.add_field(name=f"Current Level: {lvl}", value=f"{bar} **{int(progress*100)}%**", inline=False)
        embed.add_field(name="Experience", value=f"✨ `{curr:,}` / `{end:,}`", inline=True)
        embed.set_footer(text=f"Points to Level {lvl+1}: {end - curr:,} EXP")
    return embed

# --- НАСТРОЙКА БОТА ---
class LevelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Syncing commands...")
        await self.tree.sync()
        print(f"Logged in as {self.user} | Commands Synced!")

bot = LevelBot()

async def refresh_board(guild):
    gid = str(guild.id)
    if gid in active_boards:
        data = load_data()
        stats = get_stats(data, guild.id)
        try: await active_boards[gid].edit(embed=create_embed(stats, guild.name))
        except: del active_boards[gid]

@bot.tree.command(name="board", description="Показать статус уровня сервера")
async def board(interaction: discord.Interaction):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    await interaction.response.send_message(embed=create_embed(stats, interaction.guild.name))
    active_boards[str(interaction.guild_id)] = await interaction.original_response()

@bot.tree.command(name="expadd", description="Добавить опыт")
@app_commands.checks.has_permissions(administrator=True)
async def expadd(interaction: discord.Interaction, amount: int):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    stats["current"] = max(0, stats["current"] + amount)
    stats["level"] = sync_level(stats["current"])
    save_data(data)
    await interaction.response.send_message(f"✅ Добавлено {amount:,} EXP", ephemeral=True)
    await refresh_board(interaction.guild)

@bot.tree.command(name="expset", description="Установить точное количество опыта")
@app_commands.checks.has_permissions(administrator=True)
async def expset(interaction: discord.Interaction, amount: int):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    stats["current"] = max(0, amount)
    stats["level"] = sync_level(stats["current"])
    save_data(data)
    await interaction.response.send_message(f"⚙️ Опыт установлен на {amount:,}", ephemeral=True)
    await refresh_board(interaction.guild)

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive()
    # Берем токен из Environment Variables на Koyeb
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("ОШИБКА: Токен DISCORD_TOKEN не найден в настройках!")def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_stats(data, guild_id):
    gid = str(guild_id)
    if gid not in data:
        data[gid] = {"level": 0, "current": 0}
    return data[gid]

def sync_level(exp):
    lvl = 0
    for l, val in EXP_THRESHOLDS.items():
        if exp >= val: lvl = l
        else: break
    return lvl

def create_embed(stats, guild_name):
    lvl, curr = stats["level"], stats["current"]
    embed = discord.Embed(title=f"📊 Server Progress: {guild_name}", color=0x3498DB)
    
    if lvl >= MAX_LEVEL:
        bar = "🟦" * 15
        embed.add_field(name=f"Level {lvl} (MAX)", value=f"{bar} **100%**", inline=False)
        embed.add_field(name="Total Experience", value=f"💎 `{curr:,}`", inline=True)
    else:
        start, end = EXP_THRESHOLDS[lvl], EXP_THRESHOLDS[lvl+1]
        progress = min(max((curr - start) / (end - start), 0), 1.0)
        bar = "🟦" * int(progress * 15) + "⬜" * (15 - int(progress * 15))
        embed.add_field(name=f"Current Level: {lvl}", value=f"{bar} **{int(progress*100)}%**", inline=False)
        embed.add_field(name="Experience", value=f"✨ `{curr:,}` / `{end:,}`", inline=True)
        embed.set_footer(text=f"Points to Level {lvl+1}: {end - curr:,} EXP")
    return embed

# --- НАСТРОЙКА БОТА ---
class LevelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Syncing commands...")
        await self.tree.sync()
        print(f"Logged in as {self.user} | Commands Synced!")

bot = LevelBot()

async def refresh_board(guild):
    gid = str(guild.id)
    if gid in active_boards:
        data = load_data()
        stats = get_stats(data, guild.id)
        try: await active_boards[gid].edit(embed=create_embed(stats, guild.name))
        except: del active_boards[gid]

@bot.tree.command(name="board", description="Показать статус уровня сервера")
async def board(interaction: discord.Interaction):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    await interaction.response.send_message(embed=create_embed(stats, interaction.guild.name))
    active_boards[str(interaction.guild_id)] = await interaction.original_response()

@bot.tree.command(name="expadd", description="Добавить опыт")
@app_commands.checks.has_permissions(administrator=True)
async def expadd(interaction: discord.Interaction, amount: int):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    stats["current"] = max(0, stats["current"] + amount)
    stats["level"] = sync_level(stats["current"])
    save_data(data)
    await interaction.response.send_message(f"✅ Добавлено {amount:,} EXP", ephemeral=True)
    await refresh_board(interaction.guild)

@bot.tree.command(name="expset", description="Установить точное количество опыта")
@app_commands.checks.has_permissions(administrator=True)
async def expset(interaction: discord.Interaction, amount: int):
    data = load_data()
    stats = get_stats(data, interaction.guild_id)
    stats["current"] = max(0, amount)
    stats["level"] = sync_level(stats["current"])
    save_data(data)
    await interaction.response.send_message(f"⚙️ Опыт установлен на {amount:,}", ephemeral=True)
    await refresh_board(interaction.guild)

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive()
    # Берем токен из Environment Variables на Koyeb
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("ОШИБКА: Токен DISCORD_TOKEN не найден в настройках!")
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels 
            SET last_msg_id = $1, last_chan_id = $2 
            WHERE guild_id = $3
        ''', msg.id, interaction.channel_id, str(interaction.guild_id))
    
    active_boards[str(interaction.guild_id)] = msg

@bot.tree.command(name="expadd", description="Add experience to the server")
@app_commands.checks.has_permissions(administrator=True)
async def expadd(interaction: discord.Interaction, amount: int):
    stats = await get_stats(interaction.guild_id)
    new_exp = max(0, stats["current_exp"] + amount)
    new_lvl = sync_level(new_exp)
    
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels SET current_exp = $1, level = $2 WHERE guild_id = $3
        ''', new_exp, new_lvl, str(interaction.guild_id))
    
    await interaction.response.send_message(f"✅ Experience changed by {amount:,}. Current Level: {new_lvl}", ephemeral=True)
    await refresh_board(interaction.guild)

@bot.tree.command(name="expset", description="Set exact experience value")
@app_commands.checks.has_permissions(administrator=True)
async def expset(interaction: discord.Interaction, amount: int):
    new_lvl = sync_level(amount)
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels SET current_exp = $1, level = $2 WHERE guild_id = $3
        ''', amount, new_lvl, str(interaction.guild_id))
    
    await interaction.response.send_message(f"⚙️ Experience set to {amount:,}", ephemeral=True)
    await refresh_board(interaction.guild)

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        else: break
    return lvl

def create_embed(stats, guild_name):
    lvl = stats["level"]
    curr = stats["current_exp"]
    
    embed = discord.Embed(title=f"📊 Server Progress: {guild_name}", color=0x3498DB)
    
    if lvl >= MAX_LEVEL:
        bar = "🟦" * 15
        embed.add_field(name=f"Level {lvl} (MAX)", value=f"{bar} **100%**", inline=False)
        embed.add_field(name="Total Experience", value=f"💎 `{curr:,}`", inline=True)
    else:
        start, end = EXP_THRESHOLDS[lvl], EXP_THRESHOLDS[lvl+1]
        progress = min(max((curr - start) / (end - start), 0), 1.0)
        bar = "🟦" * int(progress * 15) + "⬜" * (15 - int(progress * 15))
        embed.add_field(name=f"Current Level: {lvl}", value=f"{bar} **{int(progress*100)}%**", inline=False)
        embed.add_field(name="Experience", value=f"✨ `{curr:,}` / `{end:,}`", inline=True)
        embed.set_footer(text=f"Points to Level {lvl+1}: {end - curr:,} EXP")
    return embed

# --- BOT SETUP ---
class LevelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)
        self.db_pool = None

    async def setup_hook(self):
        # Database connection using Environment Variable
        db_url = os.getenv("DATABASE_URL")
        self.db_pool = await asyncpg.create_pool(db_url)
        
        # Create table if not exists
        async with self.db_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS server_levels (
                    guild_id TEXT PRIMARY KEY,
                    level INTEGER DEFAULT 0,
                    current_exp INTEGER DEFAULT 0,
                    last_msg_id BIGINT,
                    last_chan_id BIGINT
                )
            ''')
        
        await self.tree.sync()
        print(f"Logged in as {self.user} | Commands Synced | DB Connected")

bot = LevelBot()
active_boards = {} 

async def get_stats(guild_id):
    async with bot.db_pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM server_levels WHERE guild_id = $1', str(guild_id))
        if not row:
            await conn.execute('INSERT INTO server_levels(guild_id) VALUES($1)', str(guild_id))
            row = await conn.fetchrow('SELECT * FROM server_levels WHERE guild_id = $1', str(guild_id))
        return dict(row)

async def refresh_board(guild):
    gid = str(guild.id)
    stats = await get_stats(guild.id)
    msg = active_boards.get(gid)

    # Recovery from DB if memory is empty after restart
    if not msg and stats.get("last_msg_id"):
        try:
            channel = bot.get_channel(stats["last_chan_id"]) or await bot.fetch_channel(stats["last_chan_id"])
            msg = await channel.fetch_message(stats["last_msg_id"])
            active_boards[gid] = msg
        except:
            return

    if msg:
        try:
            await msg.edit(embed=create_embed(stats, guild.name))
        except:
            if gid in active_boards: del active_boards[gid]

# --- COMMANDS ---

@bot.tree.command(name="board", description="Show server level status")
async def board(interaction: discord.Interaction):
    stats = await get_stats(interaction.guild_id)
    await interaction.response.send_message(embed=create_embed(stats, interaction.guild.name))
    msg = await interaction.original_response()
    
    # Save message info to DB
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels 
            SET last_msg_id = $1, last_chan_id = $2 
            WHERE guild_id = $3
        ''', msg.id, interaction.channel_id, str(interaction.guild_id))
    
    active_boards[str(interaction.guild_id)] = msg

@bot.tree.command(name="expadd", description="Add experience points")
@app_commands.checks.has_permissions(administrator=True)
async def expadd(interaction: discord.Interaction, amount: int):
    stats = await get_stats(interaction.guild_id)
    new_exp = max(0, stats["current_exp"] + amount)
    new_lvl = sync_level(new_exp)
    
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels SET current_exp = $1, level = $2 WHERE guild_id = $3
        ''', new_exp, new_lvl, str(interaction.guild_id))
    
    await interaction.response.send_message(f"✅ Added {amount:,} EXP", ephemeral=True)
    await refresh_board(interaction.guild)

@bot.tree.command(name="expset", description="Set total experience points")
@app_commands.checks.has_permissions(administrator=True)
async def expset(interaction: discord.Interaction, amount: int):
    new_lvl = sync_level(amount)
    async with bot.db_pool.acquire() as conn:
        await conn.execute('''
            UPDATE server_levels SET current_exp = $1, level = $2 WHERE guild_id = $3
        ''', amount, new_lvl, str(interaction.guild_id))
    
    await interaction.response.send_message(f"⚙️ Experience set to {amount:,}", ephemeral=True)
    await refresh_board(interaction.guild)

# --- RUN ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("ERROR: DISCORD_TOKEN not found!")
"__main__":
    keep_alive()
    # Берем токен из Environment Variables на Koyeb
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("ОШИБКА: Токен DISCORD_TOKEN не найден в настройках!")
