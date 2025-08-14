import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import re
import os
import urllib.parse
import time

BG_COLOR = "#000000"
FG_COLOR = "#00FF00"
FONT = ("Consolas", 11)
TITLE = "🦉 khaled.s.haddad - khaledhaddad.tech"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def show_info(title, message):
    messagebox.showinfo(title, message)

def save_to_file(filename, data):
    os.makedirs("results", exist_ok=True)
    path = os.path.join("results", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(data))))
    log_text.insert(tk.END, f"[+] Saved results to {path}\n\n")

def get_internal_links(url, domain):
    links = set()
    try:
        r = requests.get(url, timeout=10, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urllib.parse.urljoin(url, a['href'])
            if domain in href and href.startswith(("http://", "https://")):
                links.add(href)
    except Exception as e:
        log_text.insert(tk.END, f"⚠️ Failed to fetch links from {url}: {e}\n")
    return links

def harvest_emails():
    show_info("Harvest Emails", "Extracting emails from the entered domain.")
    domain_input = domain_entry.get().strip()
    if not domain_input:
        log_text.insert(tk.END, "[-] Please enter a domain.\n\n")
        return

    domain = domain_input.lower().replace("https://", "").replace("http://", "").split("/")[0]
    base_url = f"https://{domain}"
    
    log_text.insert(tk.END, f"[+] Harvesting emails from {base_url} and internal pages...\n")
    log_text.see(tk.END)

    emails = set()
    visited = set()
    queue = [
        base_url,
        f"{base_url}/contact",
        f"{base_url}/about",
        f"{base_url}/team",
        f"{base_url}/support",
        f"{base_url}/help"
    ]

    try:
        while queue:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            log_text.insert(tk.END, f"🔍 Scanning: {url}\n")
            log_text.see(tk.END)

            try:
                r = requests.get(url, timeout=10, headers=HEADERS)
                r.raise_for_status()
                new_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text))
                new_emails = {e.lower() for e in new_emails if domain in e.lower()}
                emails.update(new_emails)
                for e in new_emails:
                    log_text.insert(tk.END, f"📧 {e}\n")
                    log_text.see(tk.END)

                links = get_internal_links(url, domain)
                for link in links:
                    if link not in visited and link not in queue:
                        queue.append(link)

                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                log_text.insert(tk.END, f"❌ Failed to fetch {url}: {e}\n")
                continue

        if emails:
            log_text.insert(tk.END, f"[+] Found {len(emails)} email(s).\n")
        else:
            log_text.insert(tk.END, "[-] No emails found.\n")

        save_to_file(f"{domain}_emails.txt", list(emails))
        log_text.insert(tk.END, "[+] Harvesting completed.\n\n")

    except Exception as e:
        log_text.insert(tk.END, f"❗ Unexpected error: {e}\n\n")

def pattern_analysis():
    show_info("Pattern Analysis", "Analyzing email patterns from collected emails.")
    domain_input = domain_entry.get().strip()
    if not domain_input:
        log_text.insert(tk.END, "[-] Please enter a domain.\n\n")
        return

    domain = domain_input.lower().replace("https://", "").replace("http://", "").split("/")[0]
    path = os.path.join("results", f"{domain}_emails.txt")

    if not os.path.exists(path):
        log_text.insert(tk.END, "[-] Email file not found. Run 'Harvest Emails' first.\n\n")
        return

    with open(path, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]

    if not emails:
        log_text.insert(tk.END, "[-] No emails to analyze.\n\n")
        return

    log_text.insert(tk.END, "[+] Analyzing patterns...\n")
    patterns = set()

    for email in emails:
        local_part = email.split("@")[0].lower()
        if "." in local_part:
            patterns.add("first.last@" + domain)
        elif "_" in local_part:
            patterns.add("first_last@" + domain)
        elif len(local_part) == 2 and local_part.isalpha():
            patterns.add("f.l@" + domain)
        else:
            patterns.add("firstname@" + domain)

    for pattern in sorted(patterns):
        log_text.insert(tk.END, f"🧩 {pattern}\n")

    save_to_file(f"{domain}_patterns.txt", list(patterns))
    log_text.insert(tk.END, "[+] Pattern analysis completed.\n\n")

def profile_target():
    show_info("Target Profiling", "Gathering public info about the target.")
    domain = domain_entry.get().strip().replace("https://", "").replace("http://", "").split("/")[0]
    if not domain:
        log_text.insert(tk.END, "[-] Please enter a domain.\n\n")
        return

    log_text.insert(tk.END, "[+] Profiling target (public info only)...\n")
    dummy_info = [
        f"🏢 Company: {domain}",
        f"🌐 Website: https://{domain}",
        f"🔗 LinkedIn: https://linkedin.com/company/{domain}",
        f"🐦 Twitter: https://twitter.com/{domain.split('.')[0]}",
        f"💻 GitHub: https://github.com/{domain.split('.')[0]}"
    ]

    for info in dummy_info:
        log_text.insert(tk.END, f"{info}\n")

    save_to_file(f"{domain}_profile.txt", dummy_info)
    log_text.insert(tk.END, "[+] Profiling completed.\n\n")

def multi_step_wizard():
    log_text.insert(tk.END, "[🚀] Starting Multi-Step Wizard...\n")
    log_text.see(tk.END)
    harvest_emails()
    pattern_analysis()
    profile_target()
    log_text.insert(tk.END, "[✅] Multi-step process completed successfully!\n\n")

root = tk.Tk()
root.title(TITLE)
root.configure(bg=BG_COLOR)
root.geometry("950x650")

input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

tk.Label(input_frame, text="Enter Domain:", fg=FG_COLOR, bg=BG_COLOR, font=FONT).pack(side=tk.LEFT)
domain_entry = tk.Entry(input_frame, fg=FG_COLOR, bg=BG_COLOR, font=FONT, width=50)
domain_entry.pack(side=tk.LEFT, padx=5)

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

buttons_info = [
    ("Harvest Emails", harvest_emails),
    ("Pattern Analysis", pattern_analysis),
    ("Target Profiling", profile_target),
    ("Multi-Step Wizard", multi_step_wizard)
]

for text, func in buttons_info:
    btn = tk.Button(button_frame, text=text, fg=FG_COLOR, bg=BG_COLOR, font=FONT, width=30,
                    command=lambda f=func: threading.Thread(target=f, daemon=True).start())
    btn.pack(pady=5)

log_frame = tk.Frame(root, bg=BG_COLOR)
log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

log_text = scrolledtext.ScrolledText(log_frame, bg=BG_COLOR, fg=FG_COLOR, font=FONT, wrap=tk.WORD)
log_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
