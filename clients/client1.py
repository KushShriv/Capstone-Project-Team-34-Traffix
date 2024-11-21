import socket
import threading
import time
import logging

# Setup logging
logging.basicConfig(filename="logs/client_logs.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Function to send heartbeats every 20 seconds
def send_heartbeats(client_socket, client_name):
    while True:
        try:
            client_socket.send("HEARTBEAT".encode())
            logging.info(f"Heartbeat sent from {client_name}.")
            time.sleep(20)
        except Exception as e:
            logging.error(f"Error sending heartbeat: {e}")
            break

# Function to listen for the 4-element array from the server
def listen_for_updates(client_socket, client_name):
    output_file = f"output/{client_name}_output.txt"
    while True:
        try:
            update = client_socket.recv(1024).decode()  # Receive 4-element array
            if update:
                logging.info(f"Received update: {update}")
                with open(output_file, 'a') as f:
                    f.write(update + "\n")  # Append to the file
        except Exception as e:
            logging.error(f"Error receiving update: {e}")
            break

# Main client function
def start_client(client_name, host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(client_name.encode())  # Send client name to server

    # Start threads for sending heartbeats and listening for updates
    threading.Thread(target=send_heartbeats, args=(client_socket, client_name)).start()
    threading.Thread(target=listen_for_updates, args=(client_socket, client_name)).start()

if __name__ == "__main__":
    client_name = "client1"  # Replace with your client name
    start_client(client_name)
