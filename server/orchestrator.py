import socket
import threading
import time
import os
import logging

# Setup logging to log events to server_logs.txt
logging.basicConfig(filename="logs/orchestrator.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Dictionary to store client states and their last heartbeat time
client_data = {}

# Function to monitor and handle heartbeat of each client
def monitor_heartbeats():
    while True:
        current_time = time.time()
        for client, data in list(client_data.items()):
            if current_time - data['last_heartbeat'] > 60:  # No heartbeat for 60 seconds
                logging.info(f"Client {client} is offline.")
                client_data[client]['online'] = False
        time.sleep(10)  # Check heartbeats every 10 seconds

# Function to handle client communication
def handle_client(client_socket, client_address, client_name):
    global client_outputs
    logging.info(f"Client {client_name} connected.")
    
    # Initialize client data
    client_data[client_name] = {'last_heartbeat': time.time(), 'online': True}
    
    # Load last sent array for comparison
    last_array = None
    
    try:
        while True:
            # Receive heartbeat from client
            client_socket.settimeout(60)
            heartbeat = client_socket.recv(1024).decode()
            if heartbeat == "HEARTBEAT":
                client_data[client_name]['last_heartbeat'] = time.time()
                logging.info(f"Received heartbeat from {client_name}.")
                
                # Check for new output data to send
                output_file = f"temp/timings/timings_{client_name}.txt"
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        output_array = eval(f.read().strip())  # Assuming the file has the array format
                    
                    # Only send if output array is different from last time
                    if output_array != last_array:
                        client_socket.send(str(output_array).encode())
                        last_array = output_array
                        logging.info(f"Sent updated output to {client_name}: {output_array}")
            else:
                break
    except socket.timeout:
        logging.info(f"Client {client_name} has not sent heartbeat in 60 seconds.")
        client_data[client_name]['online'] = False
    finally:
        client_socket.close()

# Main server function
def start_server(host="127.0.0.1", port=9999):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Server started at {host}:{port}")
    
    threading.Thread(target=monitor_heartbeats).start()  # Start monitoring heartbeats
    
    while True:
        client_socket, client_address = server.accept()
        client_name = client_socket.recv(1024).decode()  # First message from client is its name
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, client_name))
        client_thread.start()

if __name__ == "__main__":
    start_server()
