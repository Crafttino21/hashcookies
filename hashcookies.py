import hashlib
import base64
import os
import time
import sys
import random
import pygame
import ctypes
from Crypto.Cipher import AES, DES, Blowfish
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2

class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def sha256_encrypt(data):
    return hashlib.sha256(data.encode()).hexdigest()

def sha512_encrypt(data):
    return hashlib.sha512(data.encode()).hexdigest()

def md5_encrypt(data):
    return hashlib.md5(data.encode()).hexdigest()

def blake2b_encrypt(data):
    return hashlib.blake2b(data.encode()).hexdigest()

def base64_encrypt(data):
    return base64.b64encode(data.encode()).decode()

def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=32)

def aes_encrypt(data, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def des_encrypt(data, key):
    iv = os.urandom(8)
    cipher = DES.new(key[:8], DES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), DES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def blowfish_encrypt(data, key):
    iv = os.urandom(8)
    cipher = Blowfish.new(key[:16], Blowfish.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), Blowfish.block_size))
    return base64.b64encode(iv + encrypted).decode()

def get_mouse_entropy():
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Move the mouse for entropy...")
    font = pygame.font.Font(None, 30)
    entropy = ""
    start_time = time.time()
    collected_points = 0
    running = True

    salt = str(time.time())

    while running:
        screen.fill((30, 30, 30))
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(5 - elapsed_time, 0)

        text_surface = font.render(f"Move the mouse! Time remaining: {remaining_time}s", True, (255, 255, 255))
        count_surface = font.render(f"Collected movements: {collected_points}", True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))
        screen.blit(count_surface, (50, 80))

        hash_preview = sha256_encrypt(entropy)[:30]
        hash_surface = font.render(f"{Colors.MAGENTA}Current hash: {hash_preview}...{Colors.RESET}", True, (255, 255, 255))
        screen.blit(hash_surface, (50, 110))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                entropy += f"{x}{y}{random.randint(0, 9)}"
                collected_points += 1
                pygame.draw.circle(screen, (255, 255, 0), (x, y), 3)

        pygame.display.flip()

        if elapsed_time >= 5:
            running = False

    pygame.quit()
    return hashlib.sha256(entropy.encode()).hexdigest() + salt

def encrypt_multiple_rounds(text, rounds, salt, password):
    key = derive_key(password, salt)
    start_time = time.time()
    for i in range(1, rounds + 1):
        text = sha256_encrypt(text)
        text = sha512_encrypt(text)
        text = md5_encrypt(text)
        text = blake2b_encrypt(text)
        text = base64_encrypt(text)
        text = aes_encrypt(text, key)
        text = des_encrypt(text, key)
        text = blowfish_encrypt(text, key)

        elapsed_time = time.time() - start_time
        eta = (elapsed_time / i) * (rounds - i)

        fancy_animation(i, rounds, text, eta)
    return text

def fancy_animation(step, total_steps, text, eta):
    progress = (step / total_steps) * 40
    bar = f"{Colors.GREEN}{'=' * int(progress)}{Colors.YELLOW}{'-' * (40 - int(progress))}{Colors.RESET}"
    eta_minutes = int(eta // 60)
    eta_seconds = int(eta % 60)
    sys.stdout.write(f"\r[{bar}] {Colors.CYAN}{step}/{total_steps}{Colors.RESET} Rounds completed | {Colors.MAGENTA}Current hash: {text[:30]}...{Colors.RESET} | {Colors.YELLOW}Remaining time: {eta_minutes}m {eta_seconds}s{Colors.RESET}")
    sys.stdout.flush()
    time.sleep(0.5)

if __name__ == "__main__":
    user_input = input(f"{Colors.BLUE}Enter a word to encrypt: {Colors.RESET}")
    password = input(f"{Colors.GREEN}Enter a password for key derivation: {Colors.RESET}")
    rounds = int(input(f"{Colors.RED}How many rounds of encryption? {Colors.RESET}"))
    print(f"{Colors.YELLOW}Collecting entropy from mouse movement...{Colors.RESET}")
    salt = get_mouse_entropy()
    print(f"{Colors.CYAN}Encryption in progress...{Colors.RESET}")
    encrypted_text = encrypt_multiple_rounds(user_input, rounds, salt, password)
    print(f"\n{Colors.BOLD}{Colors.GREEN}Done! Encrypted string:{Colors.RESET}")
    print(f"{Colors.MAGENTA}{encrypted_text}{Colors.RESET}")
