import tkinter as tk
from tkinter import scrolledtext
import threading
import imaplib
import email
from email.header import decode_header
import re
import os
from dotenv import load_dotenv
from datetime import datetime
import requests

# Load environment variables from .env file
load_dotenv()

# IMAP server credentials
username = os.getenv("EMAIL_USERNAME")
password = os.getenv("EMAIL_PASSWORD")
imap_url = "imap.gmail.com"

# Notion API credentials
notion_token = os.getenv("NOTION_TOKEN")
notion_database_id = os.getenv("NOTION_DATABASE_ID")

running = False

def authenticate_email(username, password, imap_url):
    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(username, password)
        mail.select("inbox")
        return mail
    except imaplib.IMAP4.error as e:
        return None

def fetch_job_application_emails(mail):
    try:
        status, messages = mail.search(None, 'FROM "jobs-noreply@linkedin.com" SUBJECT "Yash, your application was sent to"')
        if status != "OK":
            return []

        job_applications = []

        # Fetching emails efficiently
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(BODY.PEEK[])")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Extracting company name from subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if encoding:
                subject = subject.decode(encoding)
            else:
                subject = subject

            company_name = subject.split("Yash, your application was sent to ")[1]

            # Extracting date
            date_tuple = email.utils.parsedate_tz(msg["Date"])
            if date_tuple:
                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                email_date = local_date.strftime("%Y-%m-%d %H:%M:%S")

            # Extracting position from email body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        position_match = re.search(r'\b([A-Za-z]+ Developer)\b', body)
                        if position_match:
                            position = position_match.group(1).strip()
                            job_applications.append({
                                "company_name": company_name,
                                "position": position,
                                "email_date": email_date
                            })
                        break
            else:
                body = msg.get_payload(decode=True).decode()
                position_match = re.search(r'\b([A-Za-z]+ Developer)\b', body)
                if position_match:
                    position = position_match.group(1).strip()
                    job_applications.append({
                        "company_name": company_name,
                        "position": position,
                        "email_date": email_date
                    })

        return job_applications

    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def check_existing_entry(job_title, company_name):
    try:
        url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        data = {
            "filter": {
                "and": [
                    {
                        "property": "Job Title",
                        "title": {
                            "equals": job_title
                        }
                    },
                    {
                        "property": "Company Name",
                        "rich_text": {
                            "equals": company_name
                        }
                    }
                ]
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json().get("results", [])

        # If we get any results, it means the entry exists
        return len(results) > 0

    except requests.exceptions.RequestException as e:
        print(f"Error querying Notion database: {e}")
        return False  # Changed to False to allow adding in case of error


def add_to_notion(job_title, company_name, email_date, status="Applied"):
    if check_existing_entry(job_title, company_name):
        return None  # Entry already exists, return silently

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": { "database_id": notion_database_id },
        "properties": {
            "Job Title": {
                "title": [
                    {
                        "text": {
                            "content": job_title
                        }
                    }
                ]
            },
            "Company Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": company_name
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": email_date,
                    "end": None
                }
            },
            "Status": {
                "select": {
                    "name": status
                }
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        log_message(f"Error adding to Notion: {e}")
        return None

def run_script():
    global running
    running = True
    log_message("Starting script...")
    mail = authenticate_email(username, password, imap_url)
    if mail:
        job_applications = fetch_job_application_emails(mail)
        mail.logout()

        new_entries_count = 0
        for application in job_applications:
            if not running:
                break
            job_title = application["position"]
            company_name = application["company_name"]
            email_date = application["email_date"]
            response_code = add_to_notion(job_title, company_name, email_date)
            if response_code:
                new_entries_count += 1
                log_message(f"Added new entry: {job_title} at {company_name}")
        
        if new_entries_count > 0:
            log_message(f"Added {new_entries_count} new entries to Notion.")
        else:
            log_message("No new entries to add to Notion.")
    else:
        log_message("Failed to authenticate to email server.")
    
    log_message("Script completed.")
    running = False
    toggle_button.config(text="Start")
    root.after(5000, close_app)  # Close app after 5 seconds

def log_message(message):
    text_area.insert(tk.END, message + "\n")
    text_area.see(tk.END)

# ... (rest of the script remains the same)

def close_app():
    log_message("Closing application...")
    root.quit()

def toggle_script():
    global running
    if not running:
        threading.Thread(target=run_script, daemon=True).start()
        toggle_button.config(text="Stop")
    else:
        running = False
        log_message("Stopping script...")
        toggle_button.config(text="Start")

def log_message(message):
    text_area.insert(tk.END, message + "\n")
    text_area.see(tk.END)

# Create the main window
root = tk.Tk()
root.title("Job Application Tracker")
root.geometry("600x400")

# Create and pack the Start/Stop button
toggle_button = tk.Button(root, text="Start", command=toggle_script)
toggle_button.pack(pady=10)

# Create and pack the scrolled text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
text_area.pack(padx=10, pady=10)

# Start the GUI event loop
root.mainloop()