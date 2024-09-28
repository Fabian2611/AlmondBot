from hashlib import sha256
from pathlib import Path
import random
import sys
from time import sleep
from typing import Callable
import keyboard
from selenium import webdriver
import selenium
import selenium.common.exceptions
from selenium.webdriver import ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from termcolor import colored
from colorama import init
from settings import *
from datetime import datetime
import json

init()

answer = input("Lobby: ")

log = [f"Almond Bot v{SETTINGS["version"]}", "--------------------", f"LOG from {datetime.now().strftime('%H:%M:%S')}.\n"]

SETTINGS["lobby"] = answer if answer != "" else None

# Represents the probability of a letter appearing in a given word
# Analyzed out of dictionary.txt, can probably be improved
LETTER_DIST = {
    'a': 0.5045704444591641,
    'b': 0.14237928065178512,
    'c': 0.29490958468569917,
    'd': 0.28911373120487516,
    'e': 0.67816453600053,
    'f': 0.10463999470093396,
    'g': 0.23430151685765385,
    'h': 0.17347817447174935,
    'i': 0.547741273100616,
    'j': 0.014588991190302708,
    'k': 0.07412068622905213,
    'l': 0.3634000132476651,
    'm': 0.20027157713453003,
    'n': 0.46640060939259453,
    'o': 0.4081274425382526,
    'p': 0.21621845399748293,
    'q': 0.01579784063058886,
    'r': 0.496340332516394,
    's': 0.563373517917467,
    't': 0.46002517056368813,
    'u': 0.2527985692521693,
    'v': 0.082367357753196,
    'w': 0.07274624097502815,
    'x': 0.023481486388024112,
    'y': 0.12777372988010863,
    'z': 0.030469629727760482
}

def get_dict(param: Callable = lambda x: True) -> list[str]:
    "Returns a list of all words where param(word) is True. If no param is defined, return list of all words."
    words = []
    with open(r"C:\Users\Fabian\Desktop\Source\Data\dictionary.txt") as f:
        for line in f.readlines():
            l = line.strip().lower()
            if param(l):
                words.append(l)
    return words

def get_unique_letter_count(word: str) -> int:
    return len(set(word))

def get_unused_letter_count(word: str) -> int:
    c = 0
    for ch in word:
        if ch not in used_letters:
            c += 1
    return c

def word2score(word: str) -> int:
    # Unused Letters * 2 + Unique Letters * 2 + Length / 2 + Letter Rarity Sum
    return (get_unused_letter_count(word) * 2) + (get_unique_letter_count(word) * 2) + (len(word) / 2) + sum([1 / LETTER_DIST[ch.lower()] for ch in set(word)])

def legit_word2score(word: str) -> int:
    return get_unique_letter_count(word) * 2 - len(word)

def clean_text(text: str) -> str:
    return text.lower().replace(" ", "")

def get_best_word_with_part(part: str, key: Callable = word2score) -> str:
    "Any key function must return the highest score for the best word"
    options = []
    _part: str = clean_text(part)

    # Optional, disable for better scores, enable for faster answers
    #if _part in DICTIONARY and _part not in used_words:
    #    return _part

    for word in DICTIONARY:
        if _part in word and word not in used_words:
            options.append(word)

    if len(options) == 0:
        return None
    options.sort(key=key, reverse=True)
    return options[0]

DICTIONARY = get_dict()
# Shuffle for more human-like results
random.shuffle(DICTIONARY)

used_words = []
used_letters = []

def write(level: str, where: str, what: str, color: str = "white"):
    print(colored(f"{level.upper()}: {where} > {what}", color))

def info(what):
    write("info", "Bot", what, "blue")

def error(where, what):
    write("error", where, what, "red")
        
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--lang=en")

driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)
driver.get("https://jklm.fun/")
driver.implicitly_wait(5)
info("On site.")

if SETTINGS.get("lobby", None) == None:
    name = driver.find_element(By.XPATH, "/html/body/div/div[6]/div[2]/div[1]/div/form/div[2]/input[1]")
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located(name))
    driver.execute_script(f"arguments[0].value = '{SETTINGS.get("name", "🌰Almond Bot🌰")}';", name)
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located(name))
    info("Name entered.")

    mode = driver.find_element(By.XPATH, "/html/body/div/div[6]/div[2]/div[1]/div/form/div[1]/div[2]/label/div[1]")
    mode.click()

    driver.implicitly_wait(5)

    join = driver.find_element(By.XPATH, "/html/body/div/div[6]/div[2]/div[1]/div/form/div[2]/button")
    join.click()
    driver.implicitly_wait(5)
    WebDriverWait(driver, 100).until(EC.url_changes(driver.current_url))

else:
    driver.get(f"https://jklm.fun/{SETTINGS['lobby']}")

SETTINGS["lobby"] = driver.current_url.split('/')[-1]
info(f"Joined game. Code: {SETTINGS["lobby"]}")

name = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/form/div[2]/input")
driver.execute_script(f"arguments[0].value = '{SETTINGS.get("name", "🌰Almond Bot🌰")}';", name)
driver.implicitly_wait(5)
info("Entered name.")

start = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/form/div[2]/button")
start.click()
driver.implicitly_wait(5)
info("Now in lobby.")

driver.switch_to.frame(driver.find_element(By.XPATH,"//div[@class='game']/iframe[contains(@src,'jklm.fun')]"))
driver.implicitly_wait(5)

try:
    start = WebDriverWait(driver, 300).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='styled joinRound' and @data-text='joinGame']"))
    )
except selenium.common.exceptions.TimeoutException:
    error("Game could not start after 5 minutes.")
    driver.quit()
    exit()

start = driver.find_element(By.XPATH, "//button[contains(@class, 'styled') and @data-text='joinGame']")
start.click()
driver.implicitly_wait(5)
info("Started.")

try:
    start = WebDriverWait(driver, 300).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/button"))
    )
except:
    error("Lobby", "Nobody joined. Game ended.")
    exit()

autojoin = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/button")
autojoin.click()

info("Round starting.")

destroy = False

while True:
    info("New cycle")
    if keyboard.is_pressed("F7"):
        info("Reset used words.")
        used_words = []
    if keyboard.is_pressed("F8"):
        with open(Path(f"log-{hex(random.randint(0, 16777216))[2:]}.txt").absolute(), "x") as f:
            f.writelines(log)
            f.close()
        destroy = True
    if keyboard.is_pressed("F9") or destroy:
        info("Stopping.")
        driver.quit()
        exit()
        break
    sleep(0.01)
    try:
        enter = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[2]/form/input")
        if enter.is_displayed():
            info("Found input field.")
            text = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div").text
            info("Found syllable.")
            word = get_best_word_with_part(text)
            info("Found word.")
            used_words.append(word)
            info("Added word to used.")
            enter.send_keys(word)
            enter.send_keys(Keys.RETURN)
            info(f"Wrote {word}.")
            for ch in word:
                used_letters.append(ch)
            used_letters = list(set(used_letters))
            try:
                used_letters.remove("x")
                used_letters.remove("z")
            except:
                pass
            info(f"Used letters: {used_letters}")
            if len(used_letters) >= 24:
                info("ALL LETTERS USED.")
                used_letters = []
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Wrote '{word}'.\n")
            driver.implicitly_wait(0.2)
        else:
            pass
    except Exception as e:
        error("Main", str(type(e)) + ": " + str(e) + " in " + e.__traceback__.tb_frame.f_code.co_filename + ":" + str(e.__traceback__.tb_lineno))

    try:
        join = driver.find_element(By.XPATH, "//button[@class='styled joinRound' and @data-text='joinGame' and text()='Join game']")
        join.click()
    except:
        info("No join button.")

    # Reset round
    try:
        text = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div/header")
        if text.is_displayed():
            used_words = []
            used_letters = []
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Round over.\n")
            info("Round over.")
    except:
        pass

# TODO: Implement used letters and consider them in the score
