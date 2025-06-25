import requests
import json
import random
import string
import time
import re
from colorama import Fore, Style, init
import os
from os import system
import cloudscraper
import shutil
import threading
import fade
from threading import Event
import textwrap


term_width = shutil.get_terminal_size((80, 20)).columns
text = """
           <-. (`-')_ <-.(`-')            (`-')      (`-')  _   (`-') 
     .->      \( OO) ) __( OO)      .->   (OO )_.->  ( OO).-/<-.(OO ) 
,--.(,--.  ,--./ ,--/ '-'---.\ (`-')----. (_| \_)--.(,------.,------,)
|  | |(`-')|   \ |  | | .-. (/ ( OO).-.  '\  `.'  /  |  .---'|   /`. '
|  | |(OO )|  . '|  |)| '-' `.)( _) | |  | \    .') (|  '--. |  |_.' |
|  | | |  \|  |\    | | /`'.  | \|  |)|  | .'    \   |  .--' |  .   .'
\  '-'(_ .'|  | \   | | '--'  /  '  '-'  '/  .'.  \  |  `---.|  |\  \ 
 `-----'   `--'  `--' `------'    `-----'`--'   '--' `------'`--' '--'
                                                    
"""
gradient_colors = [Fore.RED, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE]

init(autoreset=True)

DEBUG_MODE = False

def debug_print(message):
    if DEBUG_MODE:
        print(message)

scraper = cloudscraper.create_scraper(browser={'custom': 'xkom_prod/1.123.0'})

system("title " + "Xkom Unboxer - Items rolled: 0  https://github.com/antipaster")

timeout = 40  

def load_proxy():
    try:
        with open('proxy.txt', 'r') as proxy_file:
            proxy = proxy_file.readline().strip()
            return {
                'http': proxy,
                'https': proxy
            }
    except Exception as e:
        print(f"{Fore.RED}[-] Failed to load proxy: {str(e)}")
        return None

proxy = load_proxy()

JS_FILE = 'xkom_assets.js'
API_KEY_FILE = 'api_key.txt'

api_key = "bekorcfmGwGMw9Nh"

# mozna uzywac polskich chars
polish_first_names = [
    "Jan", "Anna", "Piotr", "Katarzyna", "Marek", "Agnieszka", "Tomasz", "Maria", "Paweł", "Jolanta",
    "Adam", "Łukasz", "Michał", "Andrzej", "Krzysztof", "Wojciech", "Damian", "Bartosz", "Grzegorz", "Radosław",
    "Ewa", "Magdalena", "Elżbieta", "Monika", "Małgorzata", "Dorota", "Joanna", "Izabela", "Emilia", "Beata",
    "Zbigniew", "Aleksandra", "Rafał", "Aneta", "Mariusz", "Natalia", "Patryk", "Olga", "Wiktor", "Alicja",
    "Dariusz", "Zofia", "Sebastian", "Iwona", "Mateusz", "Teresa", "Jakub", "Karolina", "Daniel", "Sylwia"
]
# mozna uzywac polskich chars
polish_last_names = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak",
    "Majewski", "Kaczmarek", "Król", "Pawlak", "Michalski", "Jabłoński", "Piotrowski", "Stępień", "Baran",
    "Krawczyk", "Duda", "Włodarczyk", "Górski", "Wasilewski", "Ostrowski", "Sobczak", "Lis", "Makowski", "Orłowski",
    "Czarnecki", "Sikora", "Bąk", "Mazur", "Sadowski", "Chmielewski", "Szczepański", "Urbaniak", "Jasiński", "Kopeć",
    "Kołodziej", "Czerwiński", "Sosnowski", "Krupa", "Wieczorek", "Zawadzki", "Borowski", "Romanowski", "Bielawski", "Jankowski"
]


mail_providers = ['mail.tm', '1secmail']  
print('Available mail providers:')
for idx, provider in enumerate(mail_providers, 1):
    print(f"  {idx}. {provider}")
selected_provider = input('Select mail provider by number (default 1): ').strip()
if not selected_provider:
    selected_provider = '1'
try:
    selected_provider_idx = int(selected_provider) - 1
    mail_provider = mail_providers[selected_provider_idx]
except (ValueError, IndexError):
    print(f"{Fore.RED}[-] Invalid selection. Exiting.")
    exit(1)

def generate_temp_credentials():
    debug_print(f"{Fore.CYAN}[DEBUG] Starting generate_temp_credentials()")
    if mail_provider == 'mail.tm':
        email_api_url = "https://api.mail.tm/accounts"
        domain_response = requests.get("https://api.mail.tm/domains",proxies=proxy)
        debug_print(f"{Fore.CYAN}[DEBUG] Domain response status: {domain_response.status_code}")
        debug_print(f"{Fore.CYAN}[DEBUG] Domain response content: {domain_response.text[:200]}...")
        
        if domain_response.status_code == 200:
            try:
                domain_data = domain_response.json()
                debug_print(f"{Fore.CYAN}[DEBUG] Domain data: {domain_data}")
                domain = domain_data["hydra:member"][0]["domain"]
                debug_print(f"{Fore.CYAN}[DEBUG] Selected domain: {domain}")
            except json.JSONDecodeError as e:
                debug_print(f"{Fore.RED}[DEBUG] JSON decode error in domain response: {e}")
                debug_print(f"{Fore.RED}[DEBUG] Full response content: {domain_response.text}")
                raise Exception("Failed to parse domain response JSON.")
            
            email = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            account_data = {
                "address": email,
                "password": password
            }
            debug_print(f"{Fore.CYAN}[DEBUG] Creating account with data: {account_data}")
            account_response = requests.post(email_api_url, data=json.dumps(account_data), headers={"Content-Type": "application/json"},proxies=proxy)
            debug_print(f"{Fore.CYAN}[DEBUG] Account response status: {account_response.status_code}")
            debug_print(f"{Fore.CYAN}[DEBUG] Account response content: {account_response.text[:200]}...")
            
            if account_response.status_code == 201:
                print(f"{Fore.GREEN}[+] Temporary email created: {email}")
                return email, password
            else:
                raise Exception("Failed to create a temporary email account.")
        else:
            raise Exception("Failed to fetch available domains for temporary email.")
    elif mail_provider == '1secmail':
        # 1secmail domains https://www.1secmail.cc/en/page/1secmail-api
        secmail_domains = [
            '1secmail.com', '1secmail.org', '1secmail.net',
            'wwjmp.com', 'esiix.com', 'xojxe.com', 'yoggm.com', 'oosln.com'
        ]
        domain = random.choice(secmail_domains)
        login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{login}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # Not used for 1secmail
        print(f"{Fore.GREEN}[+] Temporary email created: {email}")
        return email, password
    else:
        print(f"{Fore.RED}[-] Mail provider '{mail_provider}' is not supported yet.")
        exit(1)

def get_activation_link(email, password):
    debug_print(f"{Fore.CYAN}[DEBUG] Starting get_activation_link() for email: {email}")
    if mail_provider == 'mail.tm':
        token_response = requests.post("https://api.mail.tm/token", 
                                       data=json.dumps({"address": email, "password": password}), 
                                       headers={"Content-Type": "application/json"},proxies=proxy)
        debug_print(f"{Fore.CYAN}[DEBUG] Token response status: {token_response.status_code}")
        debug_print(f"{Fore.CYAN}[DEBUG] Token response content: {token_response.text[:200]}...")
        
        if token_response.status_code == 200:
            try:
                token_data = token_response.json()
                jwt_token = token_data.get("token")
                debug_print(f"{Fore.CYAN}[DEBUG] JWT token obtained: {jwt_token[:20] if jwt_token else 'None'}...")
            except json.JSONDecodeError as e:
                debug_print(f"{Fore.RED}[DEBUG] JSON decode error in token response: {e}")
                debug_print(f"{Fore.RED}[DEBUG] Full token response content: {token_response.text}")
                raise Exception("Failed to parse token response JSON.")
            
            inbox_headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }

            time.sleep(10)

            while True:
                inbox_response = requests.get("https://api.mail.tm/messages", headers=inbox_headers)
                debug_print(f"{Fore.CYAN}[DEBUG] Inbox response status: {inbox_response.status_code}")
                debug_print(f"{Fore.CYAN}[DEBUG] Inbox response content: {inbox_response.text[:200]}...")
                
                if inbox_response.status_code == 200:
                    try:
                        inbox_data = inbox_response.json()
                        emails = inbox_data["hydra:member"]
                        debug_print(f"{Fore.CYAN}[DEBUG] Found {len(emails)} emails")
                    except json.JSONDecodeError as e:
                        debug_print(f"{Fore.RED}[DEBUG] JSON decode error in inbox response: {e}")
                        debug_print(f"{Fore.RED}[DEBUG] Full inbox response content: {inbox_response.text}")
                        raise Exception("Failed to parse inbox response JSON.")

                    if emails:
                        latest_email_id = emails[0]['id']
                        email_response = requests.get(f"https://api.mail.tm/messages/{latest_email_id}", headers=inbox_headers)
                        debug_print(f"{Fore.CYAN}[DEBUG] Email detail response status: {email_response.status_code}")
                        debug_print(f"{Fore.CYAN}[DEBUG] Email detail response content: {email_response.text[:200]}...")

                        if email_response.status_code == 200:
                            try:
                                email_detail_data = email_response.json()
                                email_body = email_detail_data["text"]
                                debug_print(f"{Fore.CYAN}[DEBUG] Email body length: {len(email_body)}")
                            except json.JSONDecodeError as e:
                                debug_print(f"{Fore.RED}[DEBUG] JSON decode error in email detail response: {e}")
                                debug_print(f"{Fore.RED}[DEBUG] Full email detail response content: {email_response.text}")
                                raise Exception("Failed to parse email detail response JSON.")

                            parts = re.split(r'(chcę dostawać newsletter|Aktywuj newsletter)', email_body)
                            if len(parts) > 1:
                                before_text = parts[0]
                                link_match = re.findall(r'https?://\S+', before_text)

                                if link_match:
                                    activation_link = link_match[-1]
                                    print(f"{Fore.GREEN}[+] Activation link found.")
                                 #   print(activation_link)
                                    return activation_link
                                else:
                                    raise Exception("No activation link found in the email body.")
                            else:
                                raise Exception("Couldn't split the email body as expected.")
                    else:
                        print(f"{Fore.YELLOW}[/] No emails found, waiting...")
                        time.sleep(10)
                else:
                    raise Exception(f"Failed to check email inbox: {inbox_response.text}")
    elif mail_provider == '1secmail':
        # 1secmail does not require password, just poll for messages
        login, domain = email.split('@')
        for _ in range(20):  #~40 seconds
            time.sleep(2)
            msg_list_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
            resp = requests.get(msg_list_url)
            if resp.status_code == 200:
                messages = resp.json()
                if messages:
                    msg_id = messages[0]['id']
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                    msg_resp = requests.get(msg_url)
                    if msg_resp.status_code == 200:
                        msg_data = msg_resp.json()
                        email_body = msg_data.get('textBody', '') + '\n' + msg_data.get('htmlBody', '')
                        parts = re.split(r'(chcę dostawać newsletter|Aktywuj newsletter)', email_body)
                        if len(parts) > 1:
                            before_text = parts[0]
                            link_match = re.findall(r'https?://\S+', before_text)
                            if link_match:
                                activation_link = link_match[-1]
                                print(f"{Fore.GREEN}[+] Activation link found.")
                                return activation_link
                            else:
                                raise Exception("No activation link found in the email body.")
                        else:
                            raise Exception("Couldn't split the email body as expected.")
                else:
                    print(f"{Fore.YELLOW}[/] No emails found, waiting...")
            else:
                print(f"{Fore.RED}[-] Failed to check 1secmail inbox: {resp.text}")
        raise Exception("No activation email received in time.")
    else:
        print(f"{Fore.RED}[-] Mail provider '{mail_provider}' is not supported yet.")
        exit(1)

def roll_box(box_id, access_token, method='put'):
    url = f"https://mobileapi.x-kom.pl/api/v1/xkom/Box/{box_id}/Items"
  #  print(url)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-API-Key": "bekorcfmGwGMw9Nh",
    }

    # debug_print(f"[DEBUG] roll_box: URL: {url}")
    # debug_print(f"[DEBUG] roll_box: Headers: {headers}")
    # debug_print(f"[DEBUG] roll_box: Proxy: {proxy}")
    # debug_print(f"[DEBUG] roll_box: Method: {method}")

    response = scraper.put(url, headers=headers, proxies=proxy)

   # debug_print(f"[DEBUG] roll_box: Status Code: {response.status_code}")
 #   debug_print(f"[DEBUG] roll_box: Response Text: {response.text}")

    try:
        data = response.json()
        debug_print(f"[DEBUG] roll_box: Response JSON: {data}")
        return data  
    except Exception as e:
        debug_print(f"[DEBUG] roll_box: Exception while parsing JSON: {e}")
        return None

item_count = 0
rolled_item_names = []
item_count_lock = threading.Lock()
update_event = Event()

use_webhook = input("Do you want to use Discord webhook? (y/n): ").strip().lower()
webhook_url = None
if use_webhook == 'y':
    webhook_url = input("Enter Discord webhook: ").strip()

thread_count = 1
try:
    thread_count = int(input("Enter number of threads to use: ").strip())
    if thread_count < 1:
        thread_count = 1
except Exception:
    print("Invalid input, using 1 thread.")

def worker():
    global item_count, rolled_item_names
    while True:
        try:
            start_time = time.time()
            email, password = generate_temp_credentials()
           # print(email)
            first_name = random.choice(polish_first_names)
            last_name = random.choice(polish_last_names)
            url = "https://mobileapi.x-kom.pl/api/v1/xkom/Account"
            headers = {
                "clientversion": "1.123.0",
                "Content-Type": "application/json; charset=UTF-8",
                "Time-Zone": "UTC",
                "x-api-key": "bekorcfmGwGMw9Nh"
            }
            data = {
                "AccountIdentity": {
                    "FirstName": "noblacklistplzzz", 
                    "LastName": "guys",  
                    "Email": email
                },
                "AccountAuthData": {
                    "Username": email,
                    "Password": password
                },
                "Consents": [
                    {
                        "Code": "offer_adaptin",
                        "IsSelected": True,
                        "IsRequested": False
                    },
                    {
                        "Code": "regulations",
                        "IsSelected": True,
                        "IsRequested": False
                    }
                ],
                "ConsentOrigin": "nw_xkom_registration"
            }
            response = scraper.post(url, headers=headers, json=data,proxies=proxy)
            print(response.text)
            if response.status_code == 200:
                token_url = "https://auth.x-kom.pl/xkom/Token"
                token_headers = {
                    "Accept-Encoding": "gzip",
                    "Connection": "Keep-Alive",
                    "Content-Length": "124",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Host": "auth.x-kom.pl",
                    "User-Agent": "xkom_prod/1.123.0"
                }
                token_data = {
                    "grant_type": "password",
                    "username": email,
                    "password": password,
                    "client_id": "android",
                    "scope": "api_v1 offline_access"
                }
                token_response = scraper.post(token_url, headers=token_headers, data=token_data,proxies=proxy)
                if token_response.status_code == 200:
                    try:
                        token_response_json = token_response.json()
                        access_token = token_response_json.get("access_token")
                    except json.JSONDecodeError:
                        continue
                    consent_url = "https://mobileapi.x-kom.pl/api/v1/xkom/Account/Consents"
                    consent_headers = {
                        "Accept-Encoding": "gzip",
                        "Authorization": f"Bearer {access_token}",
                        "clientversion": "1.123.0",
                        "Connection": "Keep-Alive",
                        "Content-Length": "114",
                        "Content-Type": "application/json; charset=UTF-8",
                        "Host": "mobileapi.x-kom.pl",
                        "Time-Zone": "UTC",
                        "User-Agent": "xkom_prod/1.123.0",
                        "x-api-key": api_key
                    }
                    consent_data = {
                        "ConsentOrigin": "nw_xkom_unbox",
                        "ConsentValues": [
                            {
                                "Code": "email_contact",
                                "IsSelected": True,
                                "IsRequested": False
                            }
                        ]
                    }
                    consent_response = scraper.put(consent_url, headers=consent_headers, data=json.dumps(consent_data))
                    try:
                        activation_link = get_activation_link(email, password)
                        if activation_link:
                            confirmation_headers = {
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            }
                            scraper.get(activation_link, headers=confirmation_headers)
                    except Exception:
                        pass
                for box_id in [1, 2, 3]:
                    box_response = roll_box(box_id, access_token)
                    if not box_response:
                        continue
                    if isinstance(box_response, dict):
                        box_rotator_id = box_response.get("BoxRotatorResourceId")
                        items = box_response.get("Items", [])
                    else:
                        continue
                    if items:
                        selected_item = random.choice(items)
                        selected_item_id = selected_item['BoxRotatorItemResourceId']
                    else:
                        continue
                    box_rotator_item_index = selected_item_id
                    stop_url = f"https://mobileapi.x-kom.pl/api/v1/xkom/Box/{box_id}/Stop?boxRotatorItemIndex={box_rotator_item_index}&rotatorSpeed={random.uniform(0.6, 1.1):.6f}"
                    stop_headers = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Authorization": f"Bearer {access_token}",
                        "box-rotator-resource-id": box_rotator_id,
                        "Connection": "keep-alive",
                        "Content-Length": "0",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Host": "mobileapi.x-kom.pl",
                        "Origin": "https://www.x-kom.pl",
                        "Referer": "https://www.x-kom.pl/",
                        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Android WebView";v="128"',
                        "sec-ch-ua-mobile": "?1",
                        "sec-ch-ua-platform": '"Android"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "time-zone": "UTC",
                        "X-API-Key": "bekorcfmGwGMw9Nh",
                        "X-Requested-With": "pl.xkom"
                    }
                    stop_response = scraper.post(stop_url, headers=stop_headers,proxies=proxy)
 
                    try:
                        stop_data = stop_response.json()
                        item = stop_data.get("Item", {})
                        item_id = item.get("Id", "N/A")
                        item_name = item.get("Name", "N/A")
                        catalog_price = item.get("CatalogPrice", "N/A")
                        photo = item.get("Photo", {})
                        image_url = photo.get("Url", "")
                        thumb_url = photo.get("ThumbnailUrl", "")
                        category = item.get("Category", {})
                        category_name = category.get("NameSingular", "N/A")
                        producer = item.get("ProducerName", "N/A")
                        box_price = stop_data.get("BoxPrice", "N/A")
                        box_rarity = stop_data.get("BoxRarity", {}).get("Name", "N/A")
                        web_url = stop_data.get("WebUrl", "")
                        expire_date = stop_data.get("ExpireDate", "N/A")
                        promo_gain = stop_data.get("PromotionGain", {})
                        promo_gain_value = promo_gain.get("Value", "N/A")
                        promo_gain_type = promo_gain.get("GainType", "N/A")
                        comments = stop_data.get("ProductCommentsStatistics", {})
                        total_comments = comments.get("TotalCount", "N/A")
                        avg_rating = comments.get("AverageRating", "N/A")
                        expiration_msg = stop_data.get("ExpirationTimeMessage", "")
                        with item_count_lock:
                            item_count += 1
                            rolled_item_names.append(item_name)
                            update_event.set()
            
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        captured_info = f"{timestamp}:{item_name}:{catalog_price}:{box_price}:{box_rarity}:{category_name}:{producer}:{promo_gain_value}:{promo_gain_type}:{email}:{password}\n"
                        with open("capture_info.txt", "a", encoding="utf-8") as file:
                            file.write(captured_info)
                        if webhook_url:
                            embed = {
                                "title": f"🎁 New Item Rolled!",
                                "description": (
                                    f"**Item:** {item_name}\n"
                                    f"**Producer:** {producer}\n"
                                    f"**Category:** {category_name}\n"
                                    f"**Box:** {box_id}\n"
                                    f"**Rarity:** {box_rarity}\n"
                                    f"**Catalog Price:** {catalog_price} zł\n"
                                    f"**Box Price:** {box_price} zł\n"
                                    f"**Promo Gain:** {promo_gain_value} {promo_gain_type}\n"
                                    f"**Expires:** {expire_date}\n"
                                    f"**Account:** `{email}`\n"
                                    f"**Password:** `{password}`\n"
                                    f"[View on x-kom]({'https://www.x-kom.pl/' + web_url if web_url else ''})"
                                ),
                                "color": 0x00ff00,
                                "footer": {"text": f"Rolled by Xkom Unboxer | {expiration_msg}"},
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                            }
                            if image_url:
                                embed["thumbnail"] = {"url": image_url}
                            discord_data = {
                                "embeds": [embed]
                            }
                            try:
                                requests.post(webhook_url, json=discord_data)
                            except Exception:
                                pass
                    except Exception:
                        continue
            else:
                try:
                    response_json = response.json()
                    if response_json.get("Errors", [{}])[0].get("Code") == "InvalidData":
                        print(f"{Fore.RED}[-] Account creation failed: Invalid data.")
                        continue
                    else:
                        print(f"{Fore.RED}[-] Account creation failed.")
                        continue
                except json.JSONDecodeError as e:
                    debug_print(f"{Fore.RED}[DEBUG] JSON decode error in account creation response: {e}")
                    debug_print(f"{Fore.RED}[DEBUG] Full account creation response content: {response.text}")
                    print(f"{Fore.RED}[-] Account creation failed - couldn't parse response.")
                    continue
        except Exception as e:
            print(f"{Fore.RED}[-] An error occurred: {str(e)}")
            continue

def print_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    centered_text = '\n'.join(line.center(term_width) for line in text.splitlines())
    faded_text = fade.brazil(centered_text)
    print(faded_text)
    count_str = f"ROLLED ITEMS: {item_count}"
    faded_count = fade.brazil(count_str.center(term_width))
    faded_sep = fade.brazil(("-" * len(count_str)).center(term_width))
    print(faded_count)
    print(faded_sep)

    item_lines = "\n".join(f"{idx}. {name}".center(term_width) for idx, name in enumerate(rolled_item_names[-15:], 1))

    if item_lines:
        print(fade.brazil(item_lines))
    print(faded_sep)


threads = []
for _ in range(thread_count):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)


try:
    print_screen()
    while True:
        update_event.wait()
        with item_count_lock:
            print_screen()
            update_event.clear()
except KeyboardInterrupt:
    pass

def gradient_text(text, colors):
    result = ""
    color_count = len(colors)
    for i, char in enumerate(text):
        if char == '\n':
            result += char
        else:
            color = colors[i % color_count]
            result += color + char
    result += Style.RESET_ALL
    return result
