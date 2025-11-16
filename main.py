import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import json
import os
from datetime import datetime, timedelta
import random

# Configuration Flask pour Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Discord en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Système de rareté avec couleurs et chances
RARETES = {
    "Typique": {"couleur": 0x808080, "chance": 40, "etoiles": "⭐"},
    "Atypique": {"couleur": 0x00FF00, "chance": 25, "etoiles": "⭐⭐"},
    "Rare": {"couleur": 0x0099FF, "chance": 15, "etoiles": "⭐⭐⭐"},
    "Épique": {"couleur": 0x9D00FF, "chance": 10, "etoiles": "⭐⭐⭐⭐"},
    "Légendaire": {"couleur": 0xFFAA00, "chance": 7, "etoiles": "⭐⭐⭐⭐⭐"},
    "Mythique": {"couleur": 0xFF0000, "chance": 2.5, "etoiles": "✨⭐⭐⭐⭐⭐✨"},
    "Spécial": {"couleur": 0xFFD700, "chance": 0.5, "etoiles": "🌟✨⭐⭐⭐⭐⭐✨🌟"}
}

# Base de données des items (images) - REMPLACEZ PAR VOS PROPRES IMAGES
ITEMS_DATABASE = {
    "Typique": [
        {"nom": "Chat Mignon", "url": "https://i.imgur.com/example1.jpg", "id": "chat_1"},
        {"nom": "Paysage Simple", "url": "https://i.imgur.com/example2.jpg", "id": "paysage_1"},
        {"nom": "Fleur Rose", "url": "https://i.imgur.com/example3.jpg", "id": "fleur_1"},
        {"nom": "Nuage Blanc", "url": "https://i.imgur.com/example4.jpg", "id": "nuage_1"},
        {"nom": "Oiseau Bleu", "url": "https://i.imgur.com/example5.jpg", "id": "oiseau_1"},
    ],
    "Atypique": [
        {"nom": "Dragon Bleu", "url": "https://i.imgur.com/example6.jpg", "id": "dragon_1"},
        {"nom": "Cascade", "url": "https://i.imgur.com/example7.jpg", "id": "cascade_1"},
        {"nom": "Loup Mystique", "url": "https://i.imgur.com/example8.jpg", "id": "loup_1"},
        {"nom": "Cristal Vert", "url": "https://i.imgur.com/example9.jpg", "id": "cristal_vert"},
    ],
    "Rare": [
        {"nom": "Phénix", "url": "https://i.imgur.com/example10.jpg", "id": "phenix_1"},
        {"nom": "Aurore Boréale", "url": "https://i.imgur.com/example11.jpg", "id": "aurore_1"},
        {"nom": "Cristal Magique", "url": "https://i.imgur.com/example12.jpg", "id": "cristal_1"},
        {"nom": "Épée Légendaire", "url": "https://i.imgur.com/example13.jpg", "id": "epee_1"},
    ],
    "Épique": [
        {"nom": "Galaxie Spirale", "url": "https://i.imgur.com/example14.jpg", "id": "galaxie_1"},
        {"nom": "Tigre Cosmique", "url": "https://i.imgur.com/example15.jpg", "id": "tigre_1"},
        {"nom": "Temple Ancien", "url": "https://i.imgur.com/example16.jpg", "id": "temple_1"},
    ],
    "Légendaire": [
        {"nom": "Portail Dimensionnel", "url": "https://i.imgur.com/example17.jpg", "id": "portail_1"},
        {"nom": "Créature Mythique", "url": "https://i.imgur.com/example18.jpg", "id": "creature_1"},
        {"nom": "Artefact Ancien", "url": "https://i.imgur.com/example19.jpg", "id": "artefact_1"},
    ],
    "Mythique": [
        {"nom": "L'Œil du Destin", "url": "https://i.imgur.com/example20.jpg", "id": "oeil_1"},
        {"nom": "Éclipse Éternelle", "url": "https://i.imgur.com/example21.jpg", "id": "eclipse_1"},
    ],
    "Spécial": [
        {"nom": "Origine du Cosmos", "url": "https://i.imgur.com/example22.jpg", "id": "cosmos_1"},
        {"nom": "Essence Divine", "url": "https://i.imgur.com/example23.jpg", "id": "essence_1"},
    ]
}

# Fichier de sauvegarde
DATA_FILE = "bot_data.json"

def load_data():
    """Charge les données depuis le fichier"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print("Erreur de lecture du fichier, création d'un nouveau fichier...")
    return {
        "users": {},
        "shop": {"items": [], "last_refresh": None},
        "battle_pass": {"season": 1, "rewards": []}
    }

def save_data():
    """Sauvegarde les données dans le fichier"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur de sauvegarde: {e}")

data = load_data()

def get_user_data(user_id):
    """Récupère ou crée les données d'un utilisateur"""
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "collection": [],
            "coins": 1000,
            "battle_pass_level": 0,
            "battle_pass_xp": 0,
            "battle_pass_premium": False,
            "last_daily": None
        }
        save_data()
    return data["users"][user_id]

def choisir_rarete():
    """Choisit une rareté basée sur les chances"""
    rand = random.uniform(0, 100)
    cumul = 0
    for rarete, info in RARETES.items():
        cumul += info["chance"]
        if rand <= cumul:
            return rarete
    return "Typique"

def generer_boutique():
    """Génère une nouvelle boutique"""
    items = []
    for _ in range(6):
        rarete = choisir_rarete()
        if ITEMS_DATABASE[rarete]:
            item = random.choice(ITEMS_DATABASE[rarete]).copy()
            item["rarete"] = rarete
            item["prix"] = {
                "Typique": 100, "Atypique": 300, "Rare": 600,
                "Épique": 1200, "Légendaire": 2500, "Mythique": 5000, "Spécial": 10000
            }[rarete]
            items.append(item)
    
    data["shop"] = {
        "items": items,
        "last_refresh": datetime.now().isoformat()
    }
    save_data()
    print(f"Boutique générée avec {len(items)} items")

@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté!')
    print(f'🤖 Bot présent sur {len(bot.guilds)} serveur(s)')
    if not data["shop"]["last_refresh"]:
        generer_boutique()
    refresh_shop.start()

@tasks.loop(hours=24)
async def refresh_shop():
    """Actualise la boutique toutes les 24h"""
    generer_boutique()
    print("🔄 Boutique actualisée!")

@bot.command(name='boutique')
async def boutique(ctx):
    """Affiche la boutique du jour"""
    shop_items = data["shop"]["items"]
    
    embed = discord.Embed(
        title="🛒 Boutique Quotidienne",
        description="La boutique se renouvelle toutes les 24 heures!",
        color=0x00FFFF,
        timestamp=datetime.now()
    )
    
    if data["shop"]["last_refresh"]:
        last_refresh = datetime.fromisoformat(data["shop"]["last_refresh"])
        next_refresh = last_refresh + timedelta(hours=24)
        time_left = next_refresh - datetime.now()
        
        if time_left.total_seconds() > 0:
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            embed.set_footer(text=f"⏰ Prochaine actualisation dans {hours}h {minutes}min")
        else:
            embed.set_footer(text="⏰ Boutique en cours d'actualisation...")
    
    for i, item in enumerate(shop_items, 1):
        rarete_info = RARETES[item["rarete"]]
        embed.add_field(
            name=f"{i}. {rarete_info['etoiles']} {item['nom']}",
            value=f"**Rareté:** {item['rarete']}\n**Prix:** {item['prix']} 💰\n`!acheter {i}`",
            inline=True
        )
    
    user_data = get_user_data(ctx.author.id)
    embed.add_field(
        name="💰 Vos Coins",
        value=f"{user_data['coins']} coins",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='acheter')
async def acheter(ctx, numero: int):
    """Achète un item de la boutique"""
    user_data = get_user_data(ctx.author.id)
    shop_items = data["shop"]["items"]
    
    if numero < 1 or numero > len(shop_items):
        await ctx.send("❌ Numéro d'item invalide! Utilisez `!boutique` pour voir les items disponibles.")
        return
    
    item = shop_items[numero - 1]
    
    # Vérifier si déjà possédé
    if any(i["id"] == item["id"] for i in user_data["collection"]):
        await ctx.send("❌ Vous possédez déjà cet item!")
        return
    
    # Vérifier les coins
    if user_data["coins"] < item["prix"]:
        await ctx.send(f"❌ Pas assez de coins! Il vous manque {item['prix'] - user_data['coins']} coins.\n💡 Utilisez `!daily` pour obtenir des coins gratuits!")
        return
    
    # Acheter l'item
    user_data["coins"] -= item["prix"]
    user_data["collection"].append(item)
    user_data["battle_pass_xp"] += 50
    
    # Vérifier level up du battle pass
    while user_data["battle_pass_xp"] >= 1000 and user_data["battle_pass_level"] < 100:
        user_data["battle_pass_xp"] -= 1000
        user_data["battle_pass_level"] += 1
    
    save_data()
    
    rarete_info = RARETES[item["rarete"]]
    embed = discord.Embed(
        title="✅ Achat réussi!",
        description=f"Vous avez acheté **{item['nom']}**!",
        color=rarete_info["couleur"]
    )
    embed.add_field(name="🎨 Rareté", value=f"{rarete_info['etoiles']} {item['rarete']}", inline=True)
    embed.add_field(name="💰 Coins restants", value=f"{user_data['coins']} coins", inline=True)
    embed.add_field(name="⭐ XP Battle Pass", value=f"+50 XP", inline=True)
    embed.set_image(url=item["url"])
    embed.set_footer(text=f"Collection: {len(user_data['collection'])} items")
    
    await ctx.send(embed=embed)

@bot.command(name='collection')
async def collection(ctx, page: int = 1):
    """Affiche votre collection"""
    user_data = get_user_data(ctx.author.id)
    
    if not user_data["collection"]:
        embed = discord.Embed(
            title="🎨 Collection vide",
            description="Vous n'avez pas encore d'items!\n\n💡 Utilisez `!boutique` pour voir les items disponibles.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"🎨 Collection de {ctx.author.display_name}",
        description=f"**Total:** {len(user_data['collection'])} items collectionnés",
        color=0xFFD700,
        timestamp=datetime.now()
    )
    
    # Compter par rareté
    raretes_count = {}
    for item in user_data["collection"]:
        rarete = item["rarete"]
        raretes_count[rarete] = raretes_count.get(rarete, 0) + 1
    
    # Afficher stats par rareté
    stats = ""
    for rarete in RARETES.keys():
        count = raretes_count.get(rarete, 0)
        if count > 0:
            stats += f"{RARETES[rarete]['etoiles']} **{rarete}**: {count}\n"
    
    embed.add_field(name="📊 Statistiques", value=stats or "Aucun item", inline=False)
    
    # Afficher quelques items
    items_display = user_data["collection"][:10]
    items_text = ""
    for item in items_display:
        rarete_info = RARETES[item["rarete"]]
        items_text += f"{rarete_info['etoiles']} {item['nom']}\n"
    
    if items_text:
        embed.add_field(name="🖼️ Items récents", value=items_text, inline=False)
    
    if len(user_data["collection"]) > 10:
        embed.add_field(name="ℹ️", value=f"Et {len(user_data['collection']) - 10} autres items...", inline=False)
    
    embed.add_field(name="💰 Coins", value=f"{user_data['coins']}", inline=True)
    embed.add_field(name="🎖️ Niveau BP", value=f"{user_data['battle_pass_level']}", inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='daily')
async def daily(ctx):
    """Récompense quotidienne"""
    user_data = get_user_data(ctx.author.id)
    
    # Vérifier si déjà réclamé aujourd'hui
    if user_data["last_daily"]:
        last_daily = datetime.fromisoformat(user_data["last_daily"])
        if datetime.now().date() == last_daily.date():
            time_left = timedelta(days=1) - (datetime.now() - last_daily)
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f"⏰ Vous avez déjà réclamé votre récompense quotidienne!\nRevenez dans {hours}h {minutes}min.")
            return
    
    # Donner la récompense
    reward = random.randint(100, 500)
    bonus_xp = 25
    user_data["coins"] += reward
    user_data["battle_pass_xp"] += bonus_xp
    user_data["last_daily"] = datetime.now().isoformat()
    
    # Level up battle pass
    level_up = False
    while user_data["battle_pass_xp"] >= 1000 and user_data["battle_pass_level"] < 100:
        user_data["battle_pass_xp"] -= 1000
        user_data["battle_pass_level"] += 1
        level_up = True
    
    save_data()
    
    embed = discord.Embed(
        title="🎁 Récompense Quotidienne",
        description=f"Vous avez reçu vos récompenses quotidiennes!",
        color=0x00FF00
    )
    embed.add_field(name="💰 Coins", value=f"+{reward} coins", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{bonus_xp} XP", inline=True)
    embed.add_field(name="💰 Total", value=f"{user_data['coins']} coins", inline=False)
    
    if level_up:
        embed.add_field(name="🎉 LEVEL UP!", value=f"Vous êtes maintenant niveau {user_data['battle_pass_level']}!", inline=False)
    
    embed.set_footer(text="Revenez demain pour une nouvelle récompense!")
    
    await ctx.send(embed=embed)

@bot.command(name='battlepass')
async def battlepass(ctx):
    """Affiche le passe de combat"""
    user_data = get_user_data(ctx.author.id)
    
    embed = discord.Embed(
        title="🎖️ Passe de Combat - Saison 1",
        description="Progressez et débloquez des récompenses exclusives!",
        color=0xFF6B00,
        timestamp=datetime.now()
    )
    
    # Barre de progression
    niveau = user_data['battle_pass_level']
    xp = user_data['battle_pass_xp']
    progress = int((xp / 1000) * 10)
    bar = "█" * progress + "░" * (10 - progress)
    
    embed.add_field(
        name=f"📊 Niveau {niveau}/100",
        value=f"{bar} {xp}/1000 XP",
        inline=False
    )
    
    embed.add_field(
        name="💎 Statut",
        value="🌟 **Premium**" if user_data['battle_pass_premium'] else "🆓 **Gratuit**",
        inline=True
    )
    
    # Récompenses à venir
    next_rewards = f"**Niveau {niveau + 1}:** Item Rare\n**Niveau {niveau + 5}:** 500 Coins\n**Niveau {niveau + 10}:** Item Épique"
    embed.add_field(
        name="🎁 Prochaines récompenses",
        value=next_rewards,
        inline=False
    )
    
    if not user_data['battle_pass_premium']:
        embed.add_field(
            name="💎 Passer Premium - 2000 coins",
            value="✨ Doublez vos récompenses\n✨ Items exclusifs\n✨ Emotes spéciaux\n\n`!acheter_bp`",
            inline=False
        )
    
    embed.set_footer(text="Gagnez de l'XP en achetant des items et en complétant votre daily!")
    
    await ctx.send(embed=embed)

@bot.command(name='acheter_bp')
async def acheter_bp(ctx):
    """Achète le passe de combat premium"""
    user_data = get_user_data(ctx.author.id)
    
    if user_data['battle_pass_premium']:
        await ctx.send("❌ Vous possédez déjà le Battle Pass Premium!")
        return
    
    if user_data['coins'] < 2000:
        await ctx.send(f"❌ Pas assez de coins! Le Battle Pass coûte 2000 coins.\nIl vous manque {2000 - user_data['coins']} coins.")
        return
    
    user_data['coins'] -= 2000
    user_data['battle_pass_premium'] = True
    save_data()
    
    embed = discord.Embed(
        title="🌟 Battle Pass Premium Débloqué!",
        description="Félicitations! Vous avez maintenant accès à toutes les récompenses premium!",
        color=0xFFD700
    )
    embed.add_field(name="✨ Avantages débloqués", value="• Récompenses doublées\n• Items exclusifs\n• Emotes spéciaux\n• Badge premium", inline=False)
    embed.set_footer(text="Merci pour votre soutien!")
    
    await ctx.send(embed=embed)

@bot.command(name='aide')
async def aide(ctx):
    """Affiche les commandes disponibles"""
    embed = discord.Embed(
        title="📖 Guide du Bot Collection",
        description="Collectionnez des images rares et progressez dans le Battle Pass!",
        color=0x3498DB
    )
    
    embed.add_field(
        name="🛒 Boutique",
        value="`!boutique` - Voir la boutique du jour\n`!acheter [numéro]` - Acheter un item",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Collection",
        value="`!collection` - Voir votre collection\n`!daily` - Récompense quotidienne (coins + XP)",
        inline=False
    )
    
    embed.add_field(
        name="🎖️ Battle Pass",
        value="`!battlepass` - Voir votre progression\n`!acheter_bp` - Acheter le Battle Pass Premium (2000 coins)",
        inline=False
    )
    
    embed.add_field(
        name="🌟 Raretés",
        value="⭐ Typique • ⭐⭐ Atypique • ⭐⭐⭐ Rare\n⭐⭐⭐⭐ Épique • ⭐⭐⭐⭐⭐ Légendaire\n✨⭐⭐⭐⭐⭐✨ Mythique • 🌟✨⭐⭐⭐⭐⭐✨🌟 Spécial",
        inline=False
    )
    
    embed.set_footer(text="La boutique se renouvelle toutes les 24 heures!")
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats(ctx):
    """Affiche les statistiques globales du bot"""
    total_users = len(data["users"])
    total_collections = sum(len(u["collection"]) for u in data["users"].values())
    
    embed = discord.Embed(
        title="📊 Statistiques du Bot",
        color=0x9B59B6
    )
    
    embed.add_field(name="👥 Utilisateurs", value=total_users, inline=True)
    embed.add_field(name="🎨 Items collectés", value=total_collections, inline=True)
    embed.add_field(name="🖥️ Serveurs", value=len(bot.guilds), inline=True)
    
    await ctx.send(embed=embed)

# Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Commande inconnue! Utilisez `!aide` pour voir les commandes disponibles.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant! Utilisez `!aide` pour voir comment utiliser cette commande.")
    else:
        print(f"Erreur: {error}")
        await ctx.send("❌ Une erreur est survenue. Veuillez réessayer.")

# Démarrage
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERREUR: Le token Discord n'est pas défini!")
        print("Ajoutez DISCORD_TOKEN dans les variables d'environnement de Render.")
    else:
        print("🚀 Démarrage du bot...")
        bot.run(TOKEN)
```

---

## 📄 **FICHIER 2 : requirements.txt**
```
discord.py==2.3.2
Flask==3.0.0
python-dotenv==1.0.0
```

---

## 📄 **FICHIER 3 : .gitignore**
```
# Fichiers de données
bot_data.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Environnement virtuel
venv/
env/
ENV/

# Variables d'environnement
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
