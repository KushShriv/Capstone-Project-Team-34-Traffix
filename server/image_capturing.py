import os
import time
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# Configure logging
log_file = 'logs/image_capturing.log'
logging.basicConfig(
    filename=log_file,  
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# List of clients and their corresponding locations
clients = {
    'client1': 'arekere',
    'client2': 'jp_nagar'
}
base_path = os.getenv("BASE_PATH")  # Base path for the HTML file
html_file = "map.html"  # Single HTML file name

# Set up options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the Chrome driver
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define a request handler for logging server
class LoggingHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        log_entry = json.loads(post_data)
        logging.info(f"{log_entry['message']}")
        self.send_response(200)
        self.end_headers()

# Start the logging server
server_address = ('', 8000)  # Port 8000 for the logging server
httpd = HTTPServer(server_address, LoggingHandler)

# Run logging server in a separate thread
import threading
logging_server_thread = threading.Thread(target=httpd.serve_forever)
logging_server_thread.daemon = True
logging_server_thread.start()

try:
    while True:  # Run indefinitely
        for client, location in clients.items():
            # Append location as a URL parameter
            file_path = os.path.join(base_path, html_file)
            url = f"file:///{file_path}?location={location}"
            
            if os.path.exists(file_path):
                driver.set_window_size(1920, 1080)
                driver.get(url)
                time.sleep(10)

                screenshot_file = f"temp/images/{client}_map.png"
                driver.save_screenshot(screenshot_file)
                logging.info(f"Screenshot taken for {client} at location '{location}': {screenshot_file}")

                # Run process_image.py asynchronously
                subprocess.Popen(['python', 'process_image.py', screenshot_file])
                logging.info(f"process_image.py started for {screenshot_file}")
                
                # Run predict.py asynchronously after process_image.py
                subprocess.Popen(['python', 'prediction.py', screenshot_file])
                logging.info(f"prediction.py started for {screenshot_file}")
            else:
                logging.warning(f"File not found: {file_path}")

        time.sleep(20)

finally:
    driver.quit()
    httpd.shutdown()
