# Client (client.py)
import socket
import threading
import signal
import os

# Global constants
HOST = '127.0.0.1'
PORT = 8888
BUFFER_SIZE = 1024

# Global variables
client_running = True

# Mutex for synchronizing console output
print_mutex = threading.Lock()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global client_running
    with print_mutex:
        print("\nDisconnecting from server...")
    client_running = False

# Thread function to receive messages from server
def receive_messages(client_socket):
    global client_running
    while client_running:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            
            message = data.decode('utf-8')
            with print_mutex:
                print(message, end='')
        except:
            break
    
    with print_mutex:
        print("\nDisconnected from server.")
    client_running = False

def main():
    global client_running
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to server
        print(f"Connecting to server at {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        
        print("Connected to server!")
        
        # Get user name
        name = input("Enter your name: ")
        
        # Send name to server
        client_socket.send(name.encode('utf-8'))
        
        # Start thread to receive messages from server
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Main loop to send messages
        while client_running:
            try:
                message = input()
                
                if not client_running:
                    break
                
                client_socket.send(message.encode('utf-8'))
            except (EOFError, KeyboardInterrupt):
                client_running = False
                break
            except Exception as e:
                print(f"Error sending message: {e}")
                client_running = False
                break
                
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        # Clean up
        try:
            client_socket.close()
        except:
            pass
        print("Disconnected from server.")

if __name__ == "__main__":
    main()