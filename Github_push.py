import subprocess  
from datetime import datetime  
import os  
import shutil

# 🔐 Ambil data dari environment  
GITHUB_ACTOR = os.getenv("GITHUB_USERNAME")  
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  
REPO = "FadhilAkbarCariearsa/Database"  
BRANCH = "main"  

def git_push():  
    try:  
        if not GITHUB_ACTOR or not GITHUB_TOKEN:  
            print("❌ GITHUB_USERNAME atau GITHUB_TOKEN tidak tersedia.")  
            return  

        auth_url = f"https://{GITHUB_ACTOR}:{GITHUB_TOKEN}@github.com/{REPO}.git"  

        # 🔄 Initialize git only if needed
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)  
            subprocess.run(["git", "config", "user.name", "ReplitBot"], check=True)  
            subprocess.run(["git", "config", "user.email", "bot@replit.com"], check=True)
        
        # Update remote if exists, otherwise add it
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["git", "remote", "set-url", "origin", auth_url], check=True)
        else:
            subprocess.run(["git", "remote", "add", "origin", auth_url], check=True)

        # 🔁 Pastikan branch sesuai
        subprocess.run(["git", "branch", "-M", BRANCH], check=True)

        subprocess.run(["git", "add", "."], check=True)  
        subprocess.run(["git", "commit", "-m", f"🔄 Auto-update: {datetime.now().isoformat()}"], check=False)  
        # Try normal push first, then pull and retry if needed
        push_result = subprocess.run(["git", "push", "origin", BRANCH], capture_output=True)
        if push_result.returncode != 0:
            subprocess.run(["git", "pull", "--rebase", "origin", BRANCH], check=False)  
            subprocess.run(["git", "push", "origin", BRANCH], check=True)
        else:
            print("🚀 Direct push successful")  

        print("✅ Push berhasil.")  
    except Exception as e:  
        print(f"❌ Push gagal: {e}")  

if __name__ == "__main__":  
    git_push()