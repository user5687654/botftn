import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import random
from flask import Flask
from threading import Thread

# Configuration Flask pour Render
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord actif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Système de rareté avec couleurs et émojis
RARITIES = {
    "Typique": {"color": 0x808080, "emoji": "⚪", "drop_rate": 40},
    "Atypique": {"color": 0x00FF00, "emoji": "🟢", "drop_rate": 25},
    "Rare": {"color": 0x0099FF, "emoji": "🔵", "drop_rate": 15},
    "Épique": {"color": 0x9932CC, "emoji": "🟣", "drop_rate": 10},
    "Légendaire": {"color": 0xFFD700, "emoji": "🟡", "drop_rate": 7},
    "Mythique": {"color": 0xFF0000, "emoji": "🔴", "drop_rate": 2.5},
    "Spécial": {"color": 0xFF1493, "emoji": "💎", "drop_rate": 0.5}
}

# Base de données (sauvegarde automatique)
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "users": {},
        "shop": {"items": [], "last_refresh": None},
        "season": {"number": 1, "start_date": datetime.now().isoformat(), "battle_pass": []},
        "items_pool": []
    }

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[{datetime.now()}] Données sauvegardées")

data = load_data()

# Initialisation des items (exemples)
def init_items():
    if not data["items_pool"]:
        items = [
            {"id": "001", "name": "Dragon de Feu", "rarity": "Légendaire", "image": "https://i.imgur.com/dragon.png", "type": "creature"},
            {"id": "002", "name": "Épée Mystique", "rarity": "Épique", "image": "https://i.imgur.com/sword.png", "type": "arme"},
            {"id": "003", "name": "Chat Mignon", "rarity": "Typique", "image": "https://i.imgur.com/cat.png", "type": "animal"},
            {"id": "004", "name": "Couronne Royale", "rarity": "Mythique", "image": "https://i.imgur.com/crown.png", "type": "accessoire"},
            {"id": "005", "name": "Potion Magique", "rarity": "Rare", "image": "https://i.imgur.com/potion.png", "type": "consommable"},
            {"id": "006", "name": "Bouclier Antique", "rarity": "Épique", "image": "https://i.imgur.com/shield.png", "type": "défense"},
            {"id": "007", "name": "Cristal de Glace", "rarity": "Légendaire", "image": "https://i.imgur.com/crystal.png", "type": "gemme"},
            {"id": "008", "name": "Arc-en-Ciel", "rarity": "Spécial", "image": "https://i.imgur.com/rainbow.png", "type": "météo"},
            {"id": "009", "name": "Loup Arctique", "rarity": "Rare", "image": "https://i.imgur.com/wolf.png", "type": "animal"},
            {"id": "010", "name": "Baguette Magique", "rarity": "Épique", "image": "https://i.imgur.com/wand.png", "type": "arme"},
            {"id": "011", "name": "Trésor Ancien", "rarity": "Mythique", "image": "https://i.imgur.com/treasure.png", "type": "objet"},
            {"id": "012", "name": "Étoile Filante", "rarity": "Spécial", "image": "https://i.imgur.com/star.png", "type": "céleste"},
            {"id": "013", "name": "Casque de Chevalier", "rarity": "Rare", "image": "https://i.imgur.com/helmet.png", "type": "armure"},
            {"id": "014", "name": "Phoenix Doré", "rarity": "Légendaire", "image": "https://i.imgur.com/phoenix.png", "type": "creature"},
            {"id": "015", "name": "Diamant Pur", "rarity": "Mythique", "image": "https://i.imgur.com/diamond.png", "type": "gemme"},
        ]
        data["items_pool"] = items
        save_data()

# Système utilisateur
def get_user(user_id):
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "collection": [],
            "l_bucks": 1000,
            "battle_pass": {"owned": False, "tier": 0, "xp": 0},
            "last_daily": None
        }
        save_data()
    return data["users"][user_id]

# Génération du passe de combat
def generate_battle_pass():
    tiers = []
    for tier in range(1, 101):
        if tier % 10 == 0:
            rarity = random.choice(["Épique", "Légendaire", "Mythique"])
        else:
            rarity = random.choice(list(RARITIES.keys()))
        
        item = random.choice([i for i in data["items_pool"] if i["rarity"] == rarity])
        tiers.append({
            "tier": tier,
            "xp_required": tier * 100,
            "free_reward": item if tier % 5 == 0 else None,
            "premium_reward": item,
            "is_premium": tier % 2 == 0
        })
    return tiers

# Génération de la boutique
def generate_shop():
    shop_items = []
    for _ in range(6):
        item = random.choice(data["items_pool"])
        rarity_info = RARITIES[item["rarity"]]
        price = {
            "Typique": 200, "Atypique": 500, "Rare": 800,
            "Épique": 1200, "Légendaire": 1500, "Mythique": 2000, "Spécial": 2500
        }[item["rarity"]]
        
        shop_items.append({**item, "price": price})
    
    data["shop"] = {
        "items": shop_items,
        "last_refresh": datetime.now().isoformat()
    }
    save_data()

# Tâche de rafraîchissement de la boutique
@tasks.loop(hours=24)
async def refresh_shop():
    generate_shop()
    print(f"[{datetime.now()}] Boutique rafraîchie!")

# Commande: Collection
@bot.tree.command(name="collection", description="Voir votre collection d'images")
async def collection(interaction: discord.Interaction):
    user_data = get_user(interaction.user.id)
    
    if not user_data["collection"]:
        embed = discord.Embed(
            title="📦 Votre Collection",
            description="Votre collection est vide! Utilisez `/boutique` ou `/passe` pour obtenir des images.",
            color=0x808080
        )
    else:
        items_by_rarity = {}
        for item_id in user_data["collection"]:
            item = next((i for i in data["items_pool"] if i["id"] == item_id), None)
            if item:
                rarity = item["rarity"]
                if rarity not in items_by_rarity:
                    items_by_rarity[rarity] = []
                items_by_rarity[rarity].append(item)
        
        embed = discord.Embed(
            title="📦 Votre Collection",
            description=f"Total: {len(user_data['collection'])} images",
            color=0x00FF00
        )
        
        for rarity in RARITIES.keys():
            if rarity in items_by_rarity:
                items = items_by_rarity[rarity]
                emoji = RARITIES[rarity]["emoji"]
                items_text = ", ".join([f"{emoji} {i['name']}" for i in items])
                embed.add_field(name=f"{rarity} ({len(items)})", value=items_text, inline=False)
    
    embed.set_footer(text=f"L-Bucks: {user_data['l_bucks']} 💰")
    await interaction.response.send_message(embed=embed)

# Commande: Boutique
@bot.tree.command(name="boutique", description="Voir la boutique du jour")
async def shop(interaction: discord.Interaction):
    if not data["shop"]["items"]:
        generate_shop()
    
    embed = discord.Embed(
        title="🏪 Boutique Quotidienne",
        description="Utilisez `/acheter <numéro>` pour acheter un item",
        color=0x3498db
    )
    
    last_refresh = datetime.fromisoformat(data["shop"]["last_refresh"])
    next_refresh = last_refresh + timedelta(hours=24)
    time_left = next_refresh - datetime.now()
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes = remainder // 60
    
    embed.add_field(name="⏰ Prochain rafraîchissement", value=f"{hours}h {minutes}m", inline=False)
    
    for idx, item in enumerate(data["shop"]["items"], 1):
        rarity_info = RARITIES[item["rarity"]]
        embed.add_field(
            name=f"{idx}. {rarity_info['emoji']} {item['name']}",
            value=f"**{item['rarity']}** • {item['price']} L-Bucks 💰",
            inline=True
        )
    
    user_data = get_user(interaction.user.id)
    embed.set_footer(text=f"Vos L-Bucks: {user_data['l_bucks']} 💰")
    await interaction.response.send_message(embed=embed)

# Commande: Acheter
@bot.tree.command(name="acheter", description="Acheter un item de la boutique")
@app_commands.describe(numero="Numéro de l'item (1-6)")
async def buy(interaction: discord.Interaction, numero: int):
    if numero < 1 or numero > len(data["shop"]["items"]):
        await interaction.response.send_message("❌ Numéro invalide!", ephemeral=True)
        return
    
    user_data = get_user(interaction.user.id)
    item = data["shop"]["items"][numero - 1]
    
    if item["id"] in user_data["collection"]:
        await interaction.response.send_message("❌ Vous possédez déjà cet item!", ephemeral=True)
        return
    
    if user_data["l_bucks"] < item["price"]:
        await interaction.response.send_message(
            f"❌ L-Bucks insuffisants! Il vous manque {item['price'] - user_data['l_bucks']} L-Bucks.",
            ephemeral=True
        )
        return
    
    user_data["l_bucks"] -= item["price"]
    user_data["collection"].append(item["id"])
    save_data()
    
    rarity_info = RARITIES[item["rarity"]]
    embed = discord.Embed(
        title="✅ Achat Réussi!",
        description=f"Vous avez acheté **{item['name']}**!",
        color=rarity_info["color"]
    )
    embed.set_image(url=item["image"])
    embed.add_field(name="Rareté", value=f"{rarity_info['emoji']} {item['rarity']}", inline=True)
    embed.add_field(name="L-Bucks restants", value=f"{user_data['l_bucks']} 💰", inline=True)
    
    await interaction.response.send_message(embed=embed)

# Commande: Passe de Combat
@bot.tree.command(name="passe", description="Voir votre progression du passe de combat")
async def battle_pass(interaction: discord.Interaction):
    user_data = get_user(interaction.user.id)
    bp = user_data["battle_pass"]
    
    if not data["season"]["battle_pass"]:
        data["season"]["battle_pass"] = generate_battle_pass()
        save_data()
    
    embed = discord.Embed(
        title=f"🎯 Passe de Combat - Saison {data['season']['number']}",
        description=f"Palier: {bp['tier']}/100 | XP: {bp['xp']}/100",
        color=0xFF6B35 if bp["owned"] else 0x808080
    )
    
    if bp["owned"]:
        embed.add_field(name="Status", value="✅ Premium", inline=True)
    else:
        embed.add_field(name="Status", value="🔒 Gratuit (Acheter pour 950 L-Bucks)", inline=True)
    
    # Afficher les 5 prochains paliers
    current_tier = bp["tier"]
    for tier_data in data["season"]["battle_pass"][current_tier:current_tier+5]:
        tier = tier_data["tier"]
        reward = tier_data["premium_reward"] if bp["owned"] else tier_data["free_reward"]
        
        if reward:
            rarity_info = RARITIES[reward["rarity"]]
            status = "✅" if tier <= current_tier else "🔒"
            embed.add_field(
                name=f"Palier {tier} {status}",
                value=f"{rarity_info['emoji']} {reward['name']}",
                inline=True
            )
    
    embed.set_footer(text="Gagnez de l'XP en étant actif sur le serveur!")
    await interaction.response.send_message(embed=embed)

# Commande: Acheter le Passe Premium
@bot.tree.command(name="acheter_passe", description="Acheter le passe de combat premium (950 L-Bucks)")
async def buy_pass(interaction: discord.Interaction):
    user_data = get_user(interaction.user.id)
    
    if user_data["battle_pass"]["owned"]:
        await interaction.response.send_message("❌ Vous possédez déjà le passe premium!", ephemeral=True)
        return
    
    if user_data["l_bucks"] < 950:
        await interaction.response.send_message(
            f"❌ L-Bucks insuffisants! Il vous manque {950 - user_data['l_bucks']} L-Bucks.",
            ephemeral=True
        )
        return
    
    user_data["l_bucks"] -= 950
    user_data["battle_pass"]["owned"] = True
    save_data()
    
    embed = discord.Embed(
        title="✨ Passe Premium Acheté!",
        description="Vous avez maintenant accès à toutes les récompenses premium!",
        color=0xFF6B35
    )
    embed.set_footer(text=f"L-Bucks restants: {user_data['l_bucks']} 💰")
    await interaction.response.send_message(embed=embed)

# Commande: Récompense Quotidienne
@bot.tree.command(name="quotidien", description="Récupérer votre récompense quotidienne")
async def daily(interaction: discord.Interaction):
    user_data = get_user(interaction.user.id)
    
    if user_data["last_daily"]:
        last_daily = datetime.fromisoformat(user_data["last_daily"])
        if datetime.now() - last_daily < timedelta(hours=24):
            time_left = timedelta(hours=24) - (datetime.now() - last_daily)
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes = remainder // 60
            await interaction.response.send_message(
                f"⏰ Revenez dans {hours}h {minutes}m pour votre prochaine récompense!",
                ephemeral=True
            )
            return
    
    reward = random.randint(100, 300)
    xp = random.randint(50, 150)
    
    user_data["l_bucks"] += reward
    user_data["battle_pass"]["xp"] += xp
    user_data["last_daily"] = datetime.now().isoformat()
    
    # Vérifier montée de niveau
    while user_data["battle_pass"]["xp"] >= 100:
        user_data["battle_pass"]["xp"] -= 100
        user_data["battle_pass"]["tier"] = min(100, user_data["battle_pass"]["tier"] + 1)
    
    save_data()
    
    embed = discord.Embed(
        title="🎁 Récompense Quotidienne!",
        description=f"Vous avez reçu:\n💰 {reward} L-Bucks\n⭐ {xp} XP",
        color=0x00FF00
    )
    embed.add_field(name="Total L-Bucks", value=f"{user_data['l_bucks']} 💰", inline=True)
    embed.add_field(name="Palier Passe", value=f"{user_data['battle_pass']['tier']}/100", inline=True)
    
    await interaction.response.send_message(embed=embed)

# Commande: Profil
@bot.tree.command(name="profil", description="Voir votre profil complet")
async def profile(interaction: discord.Interaction):
    user_data = get_user(interaction.user.id)
    
    embed = discord.Embed(
        title=f"👤 Profil de {interaction.user.display_name}",
        color=0x9B59B6
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    # Collection
    collection_count = len(user_data["collection"])
    total_items = len(data["items_pool"])
    collection_percent = (collection_count / total_items * 100) if total_items > 0 else 0
    
    embed.add_field(
        name="📦 Collection",
        value=f"{collection_count}/{total_items} ({collection_percent:.1f}%)",
        inline=True
    )
    
    # L-Bucks
    embed.add_field(
        name="💰 L-Bucks",
        value=f"{user_data['l_bucks']}",
        inline=True
    )
    
    # Passe de Combat
    bp_status = "✅ Premium" if user_data["battle_pass"]["owned"] else "🔒 Gratuit"
    embed.add_field(
        name="🎯 Passe de Combat",
        value=f"Palier {user_data['battle_pass']['tier']}/100\n{bp_status}",
        inline=True
    )
    
    # Statistiques de rareté
    rarities_owned = {}
    for item_id in user_data["collection"]:
        item = next((i for i in data["items_pool"] if i["id"] == item_id), None)
        if item:
            rarity = item["rarity"]
            rarities_owned[rarity] = rarities_owned.get(rarity, 0) + 1
    
    rarity_text = "\n".join([
        f"{RARITIES[rarity]['emoji']} {rarity}: {count}"
        for rarity, count in rarities_owned.items()
    ]) or "Aucune image collectée"
    
    embed.add_field(
        name="🌟 Par Rareté",
        value=rarity_text,
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# Commande: Info Saison
@bot.tree.command(name="saison", description="Informations sur la saison actuelle")
async def season_info(interaction: discord.Interaction):
    season = data["season"]
    start_date = datetime.fromisoformat(season["start_date"])
    days_passed = (datetime.now() - start_date).days
    
    embed = discord.Embed(
        title=f"🌟 Saison {season['number']}",
        description="Collectionnez des images exclusives!",
        color=0xE67E22
    )
    
    embed.add_field(name="📅 Jours écoulés", value=f"{days_passed} jours", inline=True)
    embed.add_field(name="🏆 Total d'items", value=f"{len(data['items_pool'])} images", inline=True)
    embed.add_field(name="👥 Joueurs actifs", value=f"{len(data['users'])} joueurs", inline=True)
    
    embed.add_field(
        name="💡 Conseil",
        value="Récupérez votre récompense `/quotidien` chaque jour!",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# Commande: Aide
@bot.tree.command(name="aide", description="Liste de toutes les commandes disponibles")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Guide des Commandes",
        description="Voici toutes les commandes disponibles:",
        color=0x3498DB
    )
    
    commands_list = [
        ("📦 `/collection`", "Voir votre collection d'images"),
        ("🏪 `/boutique`", "Voir la boutique du jour (rafraîchie toutes les 24h)"),
        ("💳 `/acheter <numéro>`", "Acheter un item de la boutique"),
        ("🎯 `/passe`", "Voir votre progression du passe de combat"),
        ("✨ `/acheter_passe`", "Acheter le passe premium (950 L-Bucks)"),
        ("🎁 `/quotidien`", "Récupérer votre récompense quotidienne"),
        ("👤 `/profil`", "Voir votre profil et statistiques"),
        ("🌟 `/saison`", "Informations sur la saison actuelle"),
        ("📚 `/aide`", "Afficher ce message d'aide"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="💰 Économie",
        value="• Départ: 1000 L-Bucks\n• Quotidien: 100-300 L-Bucks + XP\n• Prix boutique: 200-2500 L-Bucks",
        inline=False
    )
    
    embed.set_footer(text="Amusez-vous bien! 🎮")
    await interaction.response.send_message(embed=embed)

# Sauvegarde automatique toutes les 10 minutes
@tasks.loop(minutes=10)
async def auto_save():
    save_data()

# Événement: Bot prêt
@bot.event
async def on_ready():
    init_items()
    if not data["shop"]["items"]:
        generate_shop()
    
    await bot.tree.sync()
    refresh_shop.start()
    auto_save.start()
    
    print(f"✅ {bot.user} est connecté!")
    print(f"📊 Saison {data['season']['number']} active")
    print(f"👥 {len(data['users'])} utilisateurs enregistrés")
    print(f"🎨 {len(data['items_pool'])} items disponibles")

# Événement: Erreur de commande
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"❌ Erreur: {error}")

# Démarrage
if __name__ == "__main__":
    keep_alive()  # Démarre Flask pour Render
    
    # Charge le .env en local (ignoré sur Render)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ Erreur: DISCORD_TOKEN non trouvé dans les variables d'environnement!")
        print("💡 En local: Créez un fichier .env avec DISCORD_TOKEN=votre_token")
        print("💡 Sur Render: Ajoutez DISCORD_TOKEN dans Environment Variables")
    else:
        bot.run(TOKEN)
