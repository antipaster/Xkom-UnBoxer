import requests
import json
import random
import string
import time
import re
from colorama import Fore, Style, init
import os
from setproctitle import setproctitle
from os import system

init(autoreset=True)


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

def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r', encoding='utf-8') as file:
            api_key = file.read().strip()
            if api_key:
                return api_key
    
    try:
        print(f"{Fore.YELLOW}[/] Fetching xkom assets JavaScript file")
        
        cwel_headers = {
            "cache-control": "max-age=0",
            "dnt": "1",
            # 997 policja automatycznie wysla na cert.pl ze jest kradziez promek spk?
            "if-modified-since": "Fri, 11 Oct 1997 10:18:58 GMT",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="129", "Not=A?Brand";v="8"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }


        response = requests.get("https://assets.x-kom.pl/public-spa/xkom/83fbd252e70783d9.esm.min.js", headers=cwel_headers)
        
        if response.status_code == 200:
            with open(JS_FILE, 'w', encoding='utf-8') as js_file:
                js_file.write(response.text) 
            
            print(f"{Fore.GREEN}[+] JavaScript file saved: {JS_FILE}")
            
            match = re.search(r'"x-api-key":"(\w+)"', response.text)
            if match:
                api_key = match.group(1)
                

                with open(API_KEY_FILE, 'w', encoding='utf-8') as file:
                    file.write(api_key)
                
                print(f"{Fore.GREEN}[+] API key fetched and saved: {api_key}")
                return api_key
            else:
                raise Exception("API key not found in the response.")
        else:
            raise Exception("Failed to fetch JavaScript file. Status code: " + str(response.status_code))
    
    except Exception as e:
        print(f"{Fore.RED}[-] Failed to get API key: {str(e)}")
        exit(1)



api_key = get_api_key()



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

def generate_temp_credentials():
    email_api_url = "https://api.mail.tm/accounts"
    domain_response = requests.get("https://api.mail.tm/domains")
    if domain_response.status_code == 200:
        domain = domain_response.json()["hydra:member"][0]["domain"]
        email = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        account_data = {
            "address": email,
            "password": password
        }
        account_response = requests.post(email_api_url, data=json.dumps(account_data), headers={"Content-Type": "application/json"})
        if account_response.status_code == 201:
            print(f"{Fore.GREEN}[+] Temporary email created: {email}")
            return email, password
        else:
            raise Exception("Failed to create a temporary email account.")
    else:
        raise Exception("Failed to fetch available domains for temporary email.")

def get_activation_link(email, password):
    token_response = requests.post("https://api.mail.tm/token", 
                                   data=json.dumps({"address": email, "password": password}), 
                                   headers={"Content-Type": "application/json"})
    if token_response.status_code == 200:
        jwt_token = token_response.json().get("token")
        inbox_headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        time.sleep(10)

        while True:
            inbox_response = requests.get("https://api.mail.tm/messages", headers=inbox_headers)
            if inbox_response.status_code == 200:
                emails = inbox_response.json()["hydra:member"]

                if emails:
                    latest_email_id = emails[0]['id']
                    email_response = requests.get(f"https://api.mail.tm/messages/{latest_email_id}", headers=inbox_headers)

                    if email_response.status_code == 200:
                        email_body = email_response.json()["text"]

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
                    time.sleep(10)

                    if time.time() - start_time > timeout:
                        print(f"{Fore.RED}[-] No emails received within 40 seconds.")
                        break
            else:
                raise Exception(f"Failed to check email inbox: {inbox_response.text}")

item_count = 0

use_webhook = input("Do you want to use Discord webhook? (y/n): ").strip().lower()
webhook_url = None
if use_webhook == 'y':
    webhook_url = input("Enter Discord webhook: ").strip()

while True:
    try:
        start_time = time.time()
        email, password = generate_temp_credentials()
        first_name = random.choice(polish_first_names)
        last_name = random.choice(polish_last_names)
        url = "https://mobileapi.x-kom.pl/api/v1/xkom/Account"

        headers = {
            "Accept-Encoding": "gzip",
            "clientversion": "1.108.0",
            "Connection": "Keep-Alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "mobileapi.x-kom.pl",
            "Time-Zone": "UTC",
            "User-Agent": "xkom_prod/1.108.0",
            "x-api-key": api_key
        }

        data = {
            "AccountIdentity": {
                "FirstName": first_name, 
                "LastName": last_name,  
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

        response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxy)

        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] Account created successfully.")
            token_url = "https://auth.x-kom.pl/xkom/Token"
            
            token_headers = {
                "Accept-Encoding": "gzip",
                "Connection": "Keep-Alive",
                "Content-Length": "124",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "auth.x-kom.pl",
                "User-Agent": "xkom_prod/1.108.0"
            }

            token_data = {
                "grant_type": "password",
                "username": email,
                "password": password,
                "client_id": "android",
                "scope": "api_v1 offline_access"
            }

            token_response = requests.post(token_url, headers=token_headers, data=token_data)

            if token_response.status_code == 200:
                token_response_json = token_response.json()
            
                access_token = token_response_json.get("access_token")
                print(f"{Fore.GREEN}[+] Access token obtained.")

                consent_url = "https://mobileapi.x-kom.pl/api/v1/xkom/Account/Consents"
                consent_headers = {
                    "Accept-Encoding": "gzip",
                    "Authorization": f"Bearer {access_token}",
                    "clientversion": "1.108.0",
                    "Connection": "Keep-Alive",
                    "Content-Length": "114",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Host": "mobileapi.x-kom.pl",
                    "Time-Zone": "UTC",
                    "User-Agent": "xkom_prod/1.108.0",
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

                consent_response = requests.put(consent_url, headers=consent_headers, data=json.dumps(consent_data))
                print(f"{Fore.GREEN}[+] Consents updated.")

                try:
                    activation_link = get_activation_link(email, password)
                    if activation_link:
                        confirmation_headers = {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'User-Agent': 'Mozilla/5.0'
                        }
                        confirmation_response = requests.get(activation_link, headers=confirmation_headers)
                        print(f"{Fore.GREEN}[+] Account activated. Status Code: {confirmation_response.status_code}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Activation failed: {str(e)}")

            roll_urls = [
                "https://mobileapi.x-kom.pl/api/v1/xkom/Box/1/Roll",
                "https://mobileapi.x-kom.pl/api/v1/xkom/Box/2/Roll",
                "https://mobileapi.x-kom.pl/api/v1/xkom/Box/3/Roll"
            ]

            for roll_url in roll_urls:
                headers = {
                    "Accept-Encoding": "gzip",
                    "Authorization": f"Bearer {access_token}",
                    "clientversion": "1.108.0",
                    "Connection": "Keep-Alive",
                    "Content-Length": "0",
                    "Host": "mobileapi.x-kom.pl",
                    "Time-Zone": "UTC",
                    "User-Agent": "xkom_prod/1.108.0",
                    "x-api-key": "bekorcfmGwGMw9Nh" # other api key because of the box 3 that needs device to be android or ios.
                }

                response = requests.post(roll_url, headers=headers, proxies=proxy)

                if response.status_code == 200:
                    response_data = response.json()
                    item_name = response_data["Item"]["Name"]
                    promotion_gain_value = response_data["PromotionGain"]["Value"]
                    catalog_price = response_data["Item"]["CatalogPrice"]
                    photo_url = response_data["Item"]["Photo"]["Url"]  # nw po huj jak te cwele maja embedy blocked xd

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    captured_info = f"{timestamp}:{item_name}:{catalog_price}:{promotion_gain_value}:{email}:{password}\n"

                    with open("capture_info.txt", "a") as file:
                        file.write(captured_info)

                    print(f"{Fore.GREEN}[+] Item rolled: {item_name}, Promotion Gain: {promotion_gain_value}")

               
                    item_count += 1
            
                    system("title " + f"Xkom Unboxer - Items rolled: {item_count}  https://github.com/antipaster")


                    if webhook_url:
                        discord_data = {
                            "content": f"Timestamp: {timestamp}\nItem Name: {item_name}\nCatalog Price: {catalog_price}\nPromotion Gain: {promotion_gain_value}\nEmail: {email}\nPassword: {password}\nPhoto: {photo_url}"
                        }
                        requests.post(webhook_url, json=discord_data)
                else:
                    print(f"{Fore.RED}[-] Failed to roll the box at {roll_url}. Status Code: {response.status_code}")

                time.sleep(2)

            else:
                print(f"{Fore.RED}[-] Failed to get access token.")
        else:
            response_json = response.json()
            if response_json.get("Errors", [{}])[0].get("Code") == "InvalidData":
                print(f"{Fore.RED}[-] Account creation failed: Invalid data.")
                continue
            else:
                print(f"{Fore.RED}[-] Account creation failed.")
                continue
    except Exception as e:
        print(f"{Fore.RED}[-] An error occurred: {str(e)}")
        continue
