import requests
import time
import json
from datetime import datetime, timedelta
import os
from colorama import Fore, Style, init

init(autoreset=True)

def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def print_colored(text, color):
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    print(f"{colors.get(color, '')}{text}{Style.RESET_ALL}")

def get_account_info(auth_token):
    headers = {
        'authority': 'api.cspr.community',
        'accept': 'application/json',
        'authorization': f'Bearer {auth_token}',
        'content-type': 'application/json',
        'origin': 'https://webapp.cspr.community',
        'referer': 'https://webapp.cspr.community/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
    }

    response = requests.get('https://api.cspr.community/api/users/me', headers=headers)
    if response.status_code != 200:
        print_colored(f"Gagal mendapatkan info akun: {response.status_code}", 'red')
        return None

    return response.json()

def process_account(auth_token):
    account_info = get_account_info(auth_token)
    if account_info:
        user = account_info.get('user', {})
        print_colored(f"Info Akun:", 'cyan')
        print_colored(f"  Username: {user.get('username')}", 'white')
        print_colored(f"  ID: {user.get('id')}", 'white')
        print_colored(f"  Telegram UID: {user.get('telegram_uid')}", 'white')
        print_colored(f"  Bergabung pada: {user.get('joined_at')}", 'white')
        print_colored(f"  Poin: {account_info.get('points', 0)}", 'green')
        print_colored(f"  Jumlah teman: {len(account_info.get('friends', []))}", 'white')

    headers = {
        'authority': 'api.cspr.community',
        'accept': 'application/json',
        'authorization': f'Bearer {auth_token}',
        'content-type': 'application/json',
        'origin': 'https://webapp.cspr.community',
        'referer': 'https://webapp.cspr.community/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
    }

    # Mendapatkan daftar tugas
    response = requests.get('https://api.cspr.community/api/users/me/tasks', headers=headers)
    if response.status_code != 200:
        print_colored(f"Gagal mendapatkan daftar tugas: {response.status_code}", 'red')
        return

    tasks = response.json().get('tasks', {})
    all_tasks = []
    for category in tasks.values():
        all_tasks.extend(category)

    print_colored(f"Total tugas: {len(all_tasks)}", 'cyan')

    for task in all_tasks:
        task_name = task['task_name']
        print_colored(f"Memproses tugas: {task_name}", 'yellow')

        # Memulai tugas
        start_payload = {
            "task_name": task_name,
            "action": 0,
            "data": {"date": datetime.utcnow().isoformat() + "Z"}
        }
        start_response = requests.post('https://api.cspr.community/api/users/me/tasks', headers=headers, json=start_payload)
        if start_response.status_code != 200:
            print_colored(f"Gagal memulai tugas {task_name}: {start_response.status_code}", 'red')
            continue

        # Menunggu waktu yang ditentukan
        time.sleep(task['seconds_to_allow_claim'] + 1)


        # Mengklaim hadiah
        claim_payload = {
            "task_name": task_name,
            "action": 1,
            "data": {"date": datetime.utcnow().isoformat() + "Z"}
        }
        claim_response = requests.post('https://api.cspr.community/api/users/me/tasks', headers=headers, json=claim_payload)
        if claim_response.status_code != 200:
            print_colored(f"Gagal mengklaim hadiah untuk tugas {task_name}: {claim_response.status_code}", 'red')
        else:
            print_colored(f"Berhasil mengklaim hadiah untuk tugas {task_name}", 'green')

        time.sleep(1)  # Jeda singkat antara tugas

def main():
    accounts = load_accounts()
    print_colored(f"Jumlah akun: {len(accounts)}", 'magenta')

    while True:
        for i, auth_token in enumerate(accounts, 1):
            print_colored(f"Memproses akun {i}/{len(accounts)}", 'blue')
            process_account(auth_token)
            if i < len(accounts):
                print_colored("Menunggu 5 detik sebelum beralih ke akun berikutnya...", 'yellow')
                time.sleep(5)

        print_colored("Semua akun telah diproses. Menunggu 1 hari sebelum memulai ulang...", 'cyan')
        
        # Hitung mundur 1 hari
        end_time = datetime.now() + timedelta(days=1)
        while datetime.now() < end_time:
            remaining_time = end_time - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown = f"{remaining_time.days} hari {hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"\rWaktu tersisa: {countdown}", end="", flush=True)
            time.sleep(1)
        print("\nMemulai ulang proses...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_colored(f"Terjadi kesalahan: {str(e)}", 'red')
        print_colored("Melanjutkan ke tugas berikutnya...", 'yellow')
