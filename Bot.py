import discord
import json
import re
import difflib
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("log.json")
DATABASE = {}
LOG_CACHE = []

def init_files():
    global DATABASE, LOG_CACHE
    LOG_FILE.write_text("[]", encoding="utf-8")  # Clear log on boot

    try:
        with open("Database.json", "r", encoding="utf-8") as f:
            DATABASE = json.load(f)
    except:
        DATABASE = {}
        print("❌ Failed to load Database.json")

def normalize(text: str) -> str:
    # Normalize text by removing spaces and making it lowercase
    return re.sub(r"\s+", "", text.lower())

def log_query(user: discord.abc.User, query: str, matched_keys: list[str]):
    global LOG_CACHE
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": str(user),
        "user_id": user.id,
        "query": query,
        "matched_keys": matched_keys
    }
    LOG_CACHE.append(log_entry)
    
    # Maintain a reasonable cache size and write logs periodically
    if len(LOG_CACHE) >= 10:  # Write more frequently after 10 queries
        if len(LOG_CACHE) > 50:  # Keep the cache limited to the last 50 logs
            LOG_CACHE = LOG_CACHE[-50:]
        try:
            LOG_FILE.write_text(json.dumps(LOG_CACHE, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Log write error: {e}")

def search_database(query: str) -> list[tuple[str, str]]:
    if not query or not DATABASE:
        return []
    q = query.lower().strip()
    results = []
    
    # Single pass through the database with priority scoring
    for k, v in DATABASE.items():
        kl = k.lower()
        if kl == q:
            return [(k, v)]  # Exact match found, return immediately
        elif kl.startswith(q):
            results.append((0, k, v))  # Priority 0 for prefix matches
        elif q in kl:
            results.append((1, k, v))  # Priority 1 for substring matches
    
    if results:
        results.sort(key=lambda x: x[0])  # Sort by priority (prefix > contains)
        return [(k, v) for _, k, v in results]
    
    # Only use fuzzy matching if no exact/prefix/contains matches were found
    close = difflib.get_close_matches(q, DATABASE.keys(), n=3, cutoff=0.6)
    return [(k, DATABASE[k]) for k in close]

async def handle_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("?") or len(content) <= 1:
        return

    query = content[1:].strip()
    if not DATABASE:
        await message.channel.send("❌ Database is empty.")
        return

    results = search_database(query)
    if results:
        if len(results) > 10:
            results = results[:10]
            note = "\n\n📝 Showing the first 10 results."
        else:
            note = ""
        response = "\n\n".join(f"🔹 **{k}**\n{v}" for k, v in results) + note
        keys = [k for k, _ in results]
    else:
        example = ", ".join(f"`?{k}`" for k in list(DATABASE.keys())[:3])
        response = f"❌ Not found: `{query}`\n💡 Try: {example}"
        keys = []

    try:
        await message.channel.send(response)
        log_query(message.author, query, keys)
    except Exception as e:
        await message.channel.send("❌ An error occurred.")
        print(f"⚠️ {e}")