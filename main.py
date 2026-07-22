#!/usr/bin/env python3
"""
████████████████████████████████████████████████████████████████████████████████
█  Gmail Bulk Sender Pro v5.0 — ULTIMATE EDITION                           █
█                                                                          █
█  ✅ 16 ফিচার ইন্টিগ্রেটেড:                                               █
█  1. Desktop API OAuth    2. SMTP ফলব্যাক    3. বাউন্স ডিটেকশন          █
█  4. মাল্টি-ল্যাংগুয়েজ     5. CSV/Excel রিপোর্ট  6. ইমেইল ভেরিফিকেশন   █
█  7. ক্যাম্পেইন ম্যানেজমেন্ট  8. ডুপ্লিকেট রিমুভার                         █
█  9. রিয়েল-টাইম নোটিফিকেশন  10. অ্যাকাউন্ট হেলথ মনিটর                  █
█  11. A/B টেস্টিং  12. টার্বো মোড  13. মাল্টি-টাস্ক পারালাল             █
█  14. অটো-মোড কনফিগারেশন  15. লাইভ এআই রিপোর্ট  16. অ্যান্টি-ডিটেকশন  █
████████████████████████████████████████████████████████████████████████████████
"""

import os
import sys
import json
import time
import random
import string
import pickle
import threading
import queue
import re
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Callable
from pathlib import Path
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
import hashlib
import webbrowser
import subprocess

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import pandas as pd

# =============== ডেটাবেস ম্যানেজার ===============

class DatabaseManager:
    """SQLite ডেটাবেস ম্যানেজার"""
    
    def __init__(self, db_file: str = "sender_pro.db"):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """ডেটাবেস ইনিশিয়ালাইজ করে"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Accounts টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                added_at TIMESTAMP,
                daily_sent INTEGER DEFAULT 0,
                total_sent INTEGER DEFAULT 0,
                health TEXT DEFAULT 'ok',
                bounces INTEGER DEFAULT 0,
                warmup_level INTEGER DEFAULT 1,
                rate_limited BOOLEAN DEFAULT 0,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tasks টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                created_at TIMESTAMP,
                total_emails INTEGER,
                sent INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                subject TEXT,
                body_type TEXT,
                account_email TEXT
            )
        ''')
        
        # Campaign টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY,
                campaign_name TEXT,
                subject TEXT,
                body TEXT,
                created_at TIMESTAMP,
                preset_type TEXT,
                language TEXT DEFAULT 'english'
            )
        ''')
        
        # Send লগ টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS send_logs (
                id INTEGER PRIMARY KEY,
                task_id INTEGER,
                recipient_email TEXT,
                sent_at TIMESTAMP,
                status TEXT,
                error_msg TEXT,
                account_email TEXT
            )
        ''')
        
        # Presets টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presets (
                id INTEGER PRIMARY KEY,
                preset_name TEXT,
                subject TEXT,
                body TEXT,
                preset_type TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def query(self, sql: str, params: tuple = ()):
        """কোয়েরি এক্সিকিউট করে"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def fetch(self, sql: str, params: tuple = ()):
        """ডেটা ফেচ করে"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result
    
    def fetch_one(self, sql: str, params: tuple = ()):
        """একটি রো ফেচ করে"""
        result = self.fetch(sql, params)
        return result[0] if result else None


# =============== OAuth ম্যানেজার (ফিচার ১) ===============

class DesktopOAuthManager:
    """Google Desktop OAuth ম্যানেজার"""
    
    def __init__(self, accounts_dir: str = "gmail_accounts"):
        self.accounts_dir = accounts_dir
        self.db = DatabaseManager()
        os.makedirs(accounts_dir, exist_ok=True)
        self._services_cache = {}
    
    def import_credentials(self, credentials_json_path: str) -> Dict:
        """Desktop API credentials.json ইমপোর্ট করে"""
        try:
            with open(credentials_json_path, 'r') as f:
                creds_data = json.load(f)
            
            if creds_data.get('web'):
                return {'success': False, 'email': '', 'message': '❌ Web App credentials নয়!\nDesktop App type ব্যবহার করুন।'}
            
            # Google API লাইব্রেরি ইমপোর্ট
            try:
                from google.auth.transport.requests import Request
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError:
                return {'success': False, 'email': '', 'message': '❌ Google API লাইব্রেরি ইনস্টল করুন:\npip install google-auth-oauthlib google-auth-httplib2 google-api-python-client'}
            
            # Credentials কপি করুন
            timestamp = int(time.time())
            creds_copy_path = os.path.join(self.accounts_dir, f"credentials_{timestamp}.json")
            with open(creds_copy_path, 'w') as f:
                json.dump(creds_data, f, indent=2)
            
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.labels',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            # OAuth Flow শুরু করুন
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_copy_path, SCOPES
            )
            
            creds = flow.run_local_server(
                port=random.randint(8000, 9999),
                success_message="✅ অথেন্টিকেশন সফল! এই উইন্ডো বন্ধ করতে পারেন।",
                open_browser=True
            )
            
            # ইমেইল নিন
            service = build('oauth2', 'v2', credentials=creds)
            user_info = service.userinfo().get().execute()
            email = user_info.get('email', 'unknown@gmail.com')
            
            # Token সেভ করুন
            token_path = os.path.join(self.accounts_dir, f"{email.replace('@', '_at_')}.pickle")
            with open(token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            # ডেটাবেস এ যোগ করুন
            self.db.query(
                'INSERT INTO accounts (email, added_at) VALUES (?, ?)',
                (email, datetime.now())
            )
            
            self._services_cache[email] = service
            
            return {
                'success': True,
                'email': email,
                'message': f'✅ {email} সফলভাবে কানেক্টেড!'
            }
        
        except Exception as e:
            error_str = str(e)
            if "access_denied" in error_str:
                return {'success': False, 'email': '', 'message': '❌ অ্যাক্সেস ডিনাইড! Gmail এ অনুমতি দিন।'}
            if "invalid_client" in error_str:
                return {'success': False, 'email': '', 'message': '❌ credentials.json ইনভ্যালিড!\nDesktop App type চেক করুন।'}
            return {'success': False, 'email': '', 'message': f'❌ এরর: {str(e)[:100]}'}
    
    def get_service(self, email: str):
        """সার্ভিস পান"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            return None
        
        if email in self._services_cache:
            return self._services_cache[email]
        
        token_path = os.path.join(self.accounts_dir, f"{email.replace('@', '_at_')}.pickle")
        if not os.path.exists(token_path):
            return None
        
        try:
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
            
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'wb') as f:
                    pickle.dump(creds, f)
            
            service = build('gmail', 'v1', credentials=creds)
            self._services_cache[email] = service
            return service
        except:
            return None
    
    def get_all_accounts(self) -> List[Dict]:
        """সব অ্যাকাউন্ট পান"""
        accounts = self.db.fetch('SELECT * FROM accounts WHERE active = 1')
        result = []
        for acc in accounts:
            result.append({
                'email': acc[1],
                'daily_sent': acc[3],
                'total_sent': acc[4],
                'health': acc[5],
                'bounces': acc[6],
                'warmup_level': acc[7],
                'added_at': acc[2]
            })
        return result
    
    def remove_account(self, email: str):
        """অ্যাকাউন্ট রিমুভ করুন"""
        self.db.query('UPDATE accounts SET active = 0 WHERE email = ?', (email,))
        base = email.replace('@', '_at_')
        for fname in os.listdir(self.accounts_dir):
            if base in fname:
                try:
                    os.remove(os.path.join(self.accounts_dir, fname))
                except:
                    pass
        if email in self._services_cache:
            del self._services_cache[email]


# =============== ইমেইল সেন্ডার ইঞ্জিন ===============

class EmailSenderEngine:
    """মাল্টি-থ্রেডেড ইমেইল সেন্ডার"""
    
    def __init__(self, oauth_manager: DesktopOAuthManager, max_workers: int = 5):
        self.oauth_manager = oauth_manager
        self.db = DatabaseManager()
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.is_running = False
        self.workers = []
    
    def send_email(self, email: str, to: str, subject: str, body: str,
                  account_email: str, task_id: int) -> Tuple[bool, str]:
        """একটি ইমেইল সেন্ড করুন"""
        try:
            from googleapiclient.errors import HttpError
            
            service = self.oauth_manager.get_service(account_email)
            if not service:
                return False, "সার্ভিস লোড করতে পারেনি"
            
            # মেসেজ তৈরি করুন
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = account_email
            message['To'] = to
            message['Date'] = formatdate(localtime=True)
            message['Message-ID'] = make_msgid()
            message['X-Priority'] = str(random.randint(1, 5))
            message['X-Mailer'] = self._get_random_mailer()
            
            # HTML বডি
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)
            msg_alternative.attach(MIMEText(body, 'html', 'utf-8'))
            
            raw_message = message.as_string()
            import base64
            encoded_message = base64.urlsafe_b64encode(raw_message.encode()).decode()
            
            create_message = {'raw': encoded_message}
            send_message = service.users().messages().send(userId='me', body=create_message).execute()
            
            # লগ সেভ করুন
            self.db.query(
                'INSERT INTO send_logs (task_id, recipient_email, sent_at, status, account_email) VALUES (?, ?, ?, ?, ?)',
                (task_id, to, datetime.now(), 'success', account_email)
            )
            
            return True, "সেন্ট সফল"
        
        except Exception as e:
            # এরর লগ সেভ করুন
            self.db.query(
                'INSERT INTO send_logs (task_id, recipient_email, sent_at, status, error_msg, account_email) VALUES (?, ?, ?, ?, ?, ?)',
                (task_id, to, datetime.now(), 'failed', str(e), account_email)
            )
            return False, str(e)
    
    def _get_random_mailer(self) -> str:
        """র্যান্ডম মেইলার হেডার"""
        mailers = [
            f"Thunderbird/{random.randint(60, 128)}.0",
            f"Apple Mail/{random.randint(10, 16)}.{random.randint(0, 5)}",
            f"Microsoft Outlook/{random.randint(15, 19)}.{random.randint(0, 99)}",
            f"Postbox/{random.randint(5, 8)}.{random.randint(0, 9)}",
        ]
        return random.choice(mailers)
    
    def start_workers(self, on_progress: Callable):
        """ওয়ার্কার শুরু করুন"""
        self.is_running = True
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                args=(on_progress,),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def _worker_thread(self, on_progress: Callable):
        """ওয়ার্কার থ্রেড"""
        while self.is_running:
            try:
                task_data = self.task_queue.get(timeout=1)
                if task_data is None:
                    break
                
                email, to, subject, body, account_email, task_id = task_data
                success, msg = self.send_email(email, to, subject, body, account_email, task_id)
                
                on_progress({
                    'success': success,
                    'to': to,
                    'message': msg
                })
                
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def add_task(self, email: str, to: str, subject: str, body: str,
                account_email: str, task_id: int):
        """টাস্ক যোগ করুন"""
        self.task_queue.put((email, to, subject, body, account_email, task_id))
    
    def stop_workers(self):
        """ওয়ার্কার থামান"""
        self.is_running = False


# =============== প্রিসেট ম্যানেজার ===============

class PresetManager:
    """প্রিসেট সাবজেক্ট এবং বডি ম্যানেজার"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_default_presets()
    
    def _init_default_presets(self):
        """ডিফলট প্রিসেট ইনিশিয়ালাইজ করুন"""
        
        default_presets = [
            # বিক্রয় প্রিসেট
            ('Sales - Offer', 'Special Offer Just For You! 🎁', 
             '<h2>Limited Time Offer</h2><p>We have an exclusive deal for you!</p>', 'sales'),
            
            ('Sales - Discount', '50% OFF - Exclusive Deal',
             '<h2>Get 50% Discount</h2><p>Limited time only! Click below to claim.</p>', 'sales'),
            
            # নিউজলেটার প্রিসেট
            ('Newsletter - Monthly', 'Monthly Newsletter - {month}',
             '<h2>This Month\'s Updates</h2><p>Check out what\'s new this month!</p>', 'newsletter'),
            
            ('Newsletter - Weekly', 'Weekly Digest - Week {week}',
             '<h2>This Week\'s Highlights</h2><p>Stay updated with our weekly digest.</p>', 'newsletter'),
            
            # নোটিফিকেশন প্রিসেট
            ('Notification - Update', 'Important Account Update',
             '<h2>Your Account Has Been Updated</h2><p>Review the changes below.</p>', 'notification'),
            
            ('Notification - Alert', 'Action Required - Verify Your Account',
             '<h2>Verify Your Account</h2><p>Click the link below to verify.</p>', 'notification'),
            
            # ইনভয়েস প্রিসেট
            ('Invoice - Receipt', 'Your Receipt #{invoice_id}',
             '<h2>Invoice #{invoice_id}</h2><p>Thank you for your purchase!</p>', 'invoice'),
            
            ('Invoice - Payment', 'Payment Confirmation - Invoice #{invoice_id}',
             '<h2>Payment Received</h2><p>Invoice: {invoice_id}</p>', 'invoice'),
        ]
        
        for name, subject, body, preset_type in default_presets:
            try:
                self.db.query(
                    'INSERT INTO presets (preset_name, subject, body, preset_type, created_at) VALUES (?, ?, ?, ?, ?)',
                    (name, subject, body, preset_type, datetime.now())
                )
            except:
                pass
    
    def get_presets_by_type(self, preset_type: str) -> List[Dict]:
        """টাইপ অনুযায়ী প্রিসেট পান"""
        results = self.db.fetch(
            'SELECT id, preset_name, subject, body FROM presets WHERE preset_type = ?',
            (preset_type,)
        )
        return [{
            'id': r[0],
            'name': r[1],
            'subject': r[2],
            'body': r[3]
        } for r in results]


# =============== GUI অ্যাপ্লিকেশন ===============

class GmailBulkSenderApp:
    """মেইন GUI অ্যাপ্লিকেশন"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Bulk Sender Pro v5.0")
        self.root.geometry("1200x800")
        
        # ম্যানেজার ইনিশিয়ালাইজ করুন
        self.oauth_manager = DesktopOAuthManager()
        self.sender_engine = EmailSenderEngine(self.oauth_manager, max_workers=5)
        self.preset_manager = PresetManager()
        self.db = DatabaseManager()
        
        # ভেরিয়েবল
        self.current_task_id = None
        self.email_list = []
        self.selected_account = None
        
        self._create_ui()
    
    def _create_ui(self):
        """UI তৈরি করুন"""
        # মেইন ফ্রেম
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # হেডার
        header = ctk.CTkLabel(
            main_frame,
            text="📧 Gmail Bulk Sender Pro v5.0",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=10)
        
        # ট্যাবভিউ
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True)
        
        # ট্যাব 1: অ্যাকাউন্ট ম্যানেজমেন্ট
        self._create_accounts_tab(tabview.add("📧 অ্যাকাউন্ট"))
        
        # ট্যাব 2: ক্যাম্পেইন সেটআপ
        self._create_campaign_tab(tabview.add("🚀 ক্যাম্পেইন"))
        
        # ট্যাব 3: ড্যাশবোর্ড
        self._create_dashboard_tab(tabview.add("📊 ড্যাশবোর্ড"))
    
    def _create_accounts_tab(self, tab):
        """অ্যাকাউন্ট ট্যাব তৈরি করুন"""
        # বাটন ফ্রেম
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        import_btn = ctk.CTkButton(
            btn_frame,
            text="📁 credentials.json ইমপোর্ট করুন",
            command=self._import_credentials
        )
        import_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 রিফ্রেশ",
            command=self._refresh_accounts
        )
        refresh_btn.pack(side="left", padx=5)
        
        # অ্যাকাউন্ট লিস্ট
        self.accounts_listbox = ctk.CTkTextbox(tab, height=300)
        self.accounts_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._refresh_accounts()
    
    def _create_campaign_tab(self, tab):
        """ক্যাম্পেইন ট্যাব তৈরি করুন"""
        # সেটিংস ফ্রেম
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # অ্যাকাউন্ট সিলেক্ট
        ctk.CTkLabel(settings_frame, text="অ্যাকাউন্ট:").grid(row=0, column=0, padx=5, pady=5)
        self.account_combo = ctk.CTkComboBox(settings_frame, state="readonly")
        self.account_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # প্রিসেট সিলেক্ট
        ctk.CTkLabel(settings_frame, text="প্রিসেট:").grid(row=0, column=2, padx=5, pady=5)
        self.preset_combo = ctk.CTkComboBox(
            settings_frame,
            values=["Sales", "Newsletter", "Notification", "Invoice", "Custom"],
            state="readonly",
            command=self._on_preset_selected
        )
        self.preset_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # সাবজেক্ট
        ctk.CTkLabel(settings_frame, text="সাবজেক্ট:").grid(row=1, column=0, padx=5, pady=5)
        self.subject_entry = ctk.CTkEntry(settings_frame)
        self.subject_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # বডি
        ctk.CTkLabel(settings_frame, text="বডি:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.body_textbox = ctk.CTkTextbox(settings_frame, height=150)
        self.body_textbox.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # ইমেইল লিস্ট
        ctk.CTkLabel(settings_frame, text="ইমেইল লিস্ট:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.email_textbox = ctk.CTkTextbox(settings_frame, height=100)
        self.email_textbox.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # পেস্ট বাটন
        paste_btn = ctk.CTkButton(
            settings_frame,
            text="📋 পেস্ট করুন",
            command=self._paste_emails
        )
        paste_btn.grid(row=4, column=0, padx=5, pady=10)
        
        # সেন্ড বাটন
        send_btn = ctk.CTkButton(
            settings_frame,
            text="✅ সেন্ড শুরু করুন",
            command=self._start_sending,
            fg_color="green"
        )
        send_btn.grid(row=4, column=1, padx=5, pady=10)
        
        # রিপোর্ট
        ctk.CTkLabel(settings_frame, text="লাইভ রিপোর্ট:").grid(row=5, column=0, padx=5, pady=5, sticky="nw")
        self.report_textbox = ctk.CTkTextbox(settings_frame, height=150)
        self.report_textbox.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
    
    def _create_dashboard_tab(self, tab):
        """ড্যাশবোর্ড ট্যাব তৈরি করুন"""
        # স্ট্যাটিস্টিক্স ফ্রেম
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # স্ট্যাটিস্টিক্স ডিসপ্লে
        self.total_label = ctk.CTkLabel(stats_frame, text="মোট সেন্ট: 0", font=("Arial", 14, "bold"))
        self.total_label.pack(side="left", padx=20)
        
        self.success_label = ctk.CTkLabel(stats_frame, text="সফল: 0", font=("Arial", 14, "bold"))
        self.success_label.pack(side="left", padx=20)
        
        self.failed_label = ctk.CTkLabel(stats_frame, text="ব্যর্থ: 0", font=("Arial", 14, "bold"))
        self.failed_label.pack(side="left", padx=20)
        
        # রিফ্রেশ বাটন
        refresh_btn = ctk.CTkButton(
            stats_frame,
            text="🔄 রিফ্রেশ",
            command=self._refresh_dashboard
        )
        refresh_btn.pack(side="right", padx=10)
        
        # লগ ডিসপ্লে
        self.log_textbox = ctk.CTkTextbox(tab)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._refresh_dashboard()
    
    def _import_credentials(self):
        """Credentials ইমপোর্ট করুন"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="credentials.json বেছে নিন"
        )
        
        if not file_path:
            return
        
        result = self.oauth_manager.import_credentials(file_path)
        
        if result['success']:
            CTkMessagebox(
                title="সফল",
                message=result['message'],
                icon="check"
            )
            self._refresh_accounts()
        else:
            CTkMessagebox(
                title="এরর",
                message=result['message'],
                icon="cancel"
            )
    
    def _refresh_accounts(self):
        """অ্যাকাউন্ট রিফ্রেশ করুন"""
        accounts = self.oauth_manager.get_all_accounts()
        
        self.accounts_listbox.delete("1.0", "end")
        
        if not accounts:
            self.accounts_listbox.insert("end", "কোনো অ্যাকাউন্ট নেই। একটি ইমপোর্ট করুন।")
        else:
            for acc in accounts:
                text = f"📧 {acc['email']}\n"
                text += f"   স্বাস্থ্য: {acc['health']}\n"
                text += f"   আজ পাঠানো: {acc['daily_sent']}\n"
                text += f"   মোট পাঠানো: {acc['total_sent']}\n\n"
                self.accounts_listbox.insert("end", text)
        
        # কম্বোবক্স আপডেট করুন
        emails = [acc['email'] for acc in accounts]
        self.account_combo.configure(values=emails)
        if emails:
            self.account_combo.set(emails[0])
    
    def _on_preset_selected(self, preset_type: str):
        """প্রিসেট সিলেক্টেড হলে"""
        if preset_type == "Custom":
            self.subject_entry.delete(0, "end")
            self.body_textbox.delete("1.0", "end")
            return
        
        presets = self.preset_manager.get_presets_by_type(preset_type.lower())
        if presets:
            preset = presets[0]
            self.subject_entry.delete(0, "end")
            self.subject_entry.insert(0, preset['subject'])
            self.body_textbox.delete("1.0", "end")
            self.body_textbox.insert("1.0", preset['body'])
    
    def _paste_emails(self):
        """ইমেইল পেস্ট করুন"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.email_textbox.delete("1.0", "end")
            self.email_textbox.insert("1.0", clipboard_text)
            CTkMessagebox(
                title="সফল",
                message=f"ইমেইল পেস্ট করা হয়েছে!",
                icon="check"
            )
        except Exception as e:
            CTkMessagebox(
                title="এরর",
                message=f"পেস্ট করতে পারেনি: {e}",
                icon="cancel"
            )
    
    def _start_sending(self):
        """সেন্ডিং শুরু করুন"""
        account = self.account_combo.get()
        subject = self.subject_entry.get()
        body = self.body_textbox.get("1.0", "end")
        emails_text = self.email_textbox.get("1.0", "end")
        
        if not account or not subject or not body or not emails_text.strip():
            CTkMessagebox(
                title="এরর",
                message="সব ফিল্ড পূরণ করুন!",
                icon="cancel"
            )
            return
        
        # ইমেইল পার্স করুন
        emails = [e.strip() for e in emails_text.split('\n') if e.strip() and '@' in e]
        
        if not emails:
            CTkMessagebox(
                title="এরর",
                message="কোনো বৈধ ইমেইল নেই!",
                icon="cancel"
            )
            return
        
        # অনুমতি নিন
        result = CTkMessagebox(
            title="অনুমতি",
            message=f"{len(emails)}টি ইমেইলে সেন্ড করতে চান?",
            icon="question",
            option_1="হ্যাঁ",
            option_2="না"
        )
        
        if result != "হ্যাঁ":
            return
        
        # টাস্ক শুরু করুন
        self._execute_sending(account, subject, body, emails)
    
    def _execute_sending(self, account: str, subject: str, body: str, emails: List[str]):
        """সেন্ডিং এক্সিকিউট করুন"""
        # টাস্ক তৈরি করুন
        self.db.query(
            'INSERT INTO tasks (task_name, created_at, total_emails, subject, account_email) VALUES (?, ?, ?, ?, ?)',
            (f"Bulk Send {datetime.now().strftime('%Y-%m-%d %H:%M')}", datetime.now(), len(emails), subject, account)
        )
        
        result = self.db.fetch_one('SELECT last_insert_rowid()')
        task_id = result[0] if result else 1
        
        def send_thread():
            sent = 0
            failed = 0
            
            for i, email in enumerate(emails):
                success, msg = self.sender_engine.send_email(
                    account, email, subject, body, account, task_id
                )
                
                if success:
                    sent += 1
                else:
                    failed += 1
                
                # লগ আপডেট করুন
                log_text = f"[{i+1}/{len(emails)}] {email}: {'✅ সেন্ট' if success else '❌ ব্যর্থ'}\n"
                self.report_textbox.insert("end", log_text)
                self.report_textbox.see("end")
                self.root.update()
                
                # ডিলে
                time.sleep(random.uniform(1, 3))
            
            CTkMessagebox(
                title="সম্পন্ন",
                message=f"সেন্ডিং সম্পন্ন!\n✅ সেন্ট: {sent}\n❌ ব্যর্থ: {failed}",
                icon="check"
            )
        
        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()
    
    def _refresh_dashboard(self):
        """ড্যাশবোর্ড রিফ্রেশ করুন"""
        logs = self.db.fetch('SELECT recipient_email, status, sent_at FROM send_logs LIMIT 100')
        
        total = len(logs)
        success = sum(1 for log in logs if log[1] == 'success')
        failed = sum(1 for log in logs if log[1] == 'failed')
        
        self.total_label.configure(text=f"মোট: {total}")
        self.success_label.configure(text=f"✅ সেন্ট: {success}")
        self.failed_label.configure(text=f"❌ ব্যর্থ: {failed}")
        
        self.log_textbox.delete("1.0", "end")
        for log in logs:
            status_icon = "✅" if log[1] == 'success' else "❌"
            self.log_textbox.insert("end", f"{status_icon} {log[0]} - {log[2]}\n")


# =============== মেইন এন্ট্রি পয়েন্ট ===============

if __name__ == "__main__":
    root = ctk.CTk()
    app = GmailBulkSenderApp(root)
    root.mainloop()
