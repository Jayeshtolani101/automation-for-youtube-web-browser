import tkinter as tk
from tkinter import messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import threading
import time
import os
import pandas as pd

stop_threads = False

def open_and_close_browser(duration, url, proxy=None):
    global stop_threads
    try:
        # Ensure the path to chromedriver.exe is correct
        chromedriver_path = r"C:\Users\jayes\Desktop\new\chromedriver\chromedriver.exe"
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"Chromedriver executable not found at {chromedriver_path}")
        
        chrome_options = webdriver.ChromeOptions()
        if proxy:
            print(f"Using proxy: {proxy}")  # Debug print
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        for _ in range(duration):
            if stop_threads:
                break
            time.sleep(1)
        driver.quit()
    except Exception as e:
        print(f"Error: {e}")

def start_browsers():
    global stop_threads
    stop_threads = False
    try:
        count = int(entry_count.get())
        duration = int(entry_duration.get())
        url = entry_url.get()
        proxy_file_path = entry_proxy.get()

        if count <= 0 or duration <= 0:
            print("Count and duration must be positive integers.")
            return

        if not url:
            print("URL must be provided.")
            return

        if not os.path.exists(proxy_file_path):
            print("Proxy file not found.")
            return

        proxies = pd.read_excel(proxy_file_path).iloc[:, 0].tolist()
        print(f"Proxies loaded: {proxies}")  # Debug print
        if len(proxies) < count:
            print("Not enough proxies in the file.")
            return

        threads = []
        for i in range(count):
            proxy = proxies[i % len(proxies)]
            print(f"Starting browser with proxy: {proxy}")  # Debug print
            t = threading.Thread(target=open_and_close_browser, args=(duration, url, proxy))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
    except Exception as e:
        print(f"Error: {e}")

def stop_browsers():
    global stop_threads
    stop_threads = True
    root.quit()
    root.destroy()

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    entry_proxy.delete(0, tk.END)
    entry_proxy.insert(0, filename)

# GUI setup
root = tk.Tk()
root.title("Browser Automation")

tk.Label(root, text="Number of Browsers:").grid(row=0)
tk.Label(root, text="Duration (seconds):").grid(row=1)
tk.Label(root, text="URL:").grid(row=2)
tk.Label(root, text="Proxy File (Excel):").grid(row=3)

entry_count = tk.Entry(root)
entry_duration = tk.Entry(root)
entry_url = tk.Entry(root)
entry_proxy = tk.Entry(root)

entry_count.grid(row=0, column=1)
entry_duration.grid(row=1, column=1)
entry_url.grid(row=2, column=1)
entry_proxy.grid(row=3, column=1)

tk.Button(root, text='Browse', command=browse_file).grid(row=3, column=2, sticky=tk.W, pady=4)
tk.Button(root, text='Start', command=start_browsers).grid(row=4, column=1, sticky=tk.W, pady=4)
tk.Button(root, text='Exit', command=stop_browsers).grid(row=4, column=2, sticky=tk.W, pady=4)

root.mainloop()