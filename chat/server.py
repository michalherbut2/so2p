# Server (server.py)
import socket
import threading
import signal
import sys

# Global constants
HOST = '127.0.0.1'
PORT = 8888
BUFFER_SIZE = 1024
MAX_CLIENTS = 10

# Global variables
server_running = True
clients = []  # List of client sockets
client_names = {}  # Dictionary mapping sockets to client names

# Mutex for synchronizing access to shared resources
clients_mutex = threading.Lock()
print_mutex = threading.Lock()

# Message queue with synchronization
class MessageQueue:
    def __init__(self):
        self.messages = []
        self.queue_mutex = threading.Lock()
        self.not_empty = threading.Condition(self.queue_mutex)

    def enqueue(self, client_socket, message):
        with self.queue_mutex:
            self.messages.append((client_socket, message))
            self.not_empty.notify()

    def dequeue(self):
        with self.not_empty:
            while not self.messages and server_running:
                self.not_empty.wait(0.1)  # Wait with timeout to check server_running
            if not server_running:
                return None, None
            if self.messages:
                return self.messages.pop(0)
            return None, None

# Initialize message queue
message_queue = MessageQueue()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global server_running
    with print_mutex:
        print("\nShutting down server...")
    server_running = False
    # Close all client connections
    with clients_mutex:
        for client in clients:
            try:
                client.close()
            except:
                pass

# Add a client to the clients list
def add_client(client_socket, client_name):
    with clients_mutex:
        if len(clients) < MAX_CLIENTS:
            clients.append(client_socket)
            client_names[client_socket] = client_name
            return True
        return False

# Remove a client from the clients list
def remove_client(client_socket):
    with clients_mutex:
        if client_socket in clients:
            clients.remove(client_socket)
            client_name = client_names.pop(client_socket, "Unknown")
            return client_name
    return None

# Broadcast message to all clients except sender
def broadcast_message(sender_socket, message):
    with clients_mutex:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # If sending fails, client might be disconnected
                    pass

# Thread function to handle a client
def handle_client(client_socket, client_address):
    try:
        # Receive client name
        name_data = client_socket.recv(BUFFER_SIZE)
        if not name_data:
            client_socket.close()
            return
        
        client_name = name_data.decode('utf-8')
        
        # Add client to the list
        if not add_client(client_socket, client_name):
            # Server is full
            client_socket.send("Server is full. Please try again later.\n".encode('utf-8'))
            client_socket.close()
            return
        
        # Notify all clients that a new user has joined
        welcome_message = f"SERVER: {client_name} has joined the chat.\n"
        message_queue.enqueue(client_socket, welcome_message)
        
        with print_mutex:
            print(welcome_message, end='')
        
        # Main loop to receive messages from this client
        while server_running:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                message = data.decode('utf-8')
                formatted_message = f"{client_name}: {message}\n"
                
                # Add message to queue
                message_queue.enqueue(client_socket, formatted_message)
                
                with print_mutex:
                    print(formatted_message, end='')
                    
            except:
                break
    finally:
        # Client disconnected
        client_name = remove_client(client_socket)
        if client_name:
            leave_message = f"SERVER: {client_name} has left the chat.\n"
            message_queue.enqueue(None, leave_message)
            with print_mutex:
                print(leave_message, end='')
        
        try:
            client_socket.close()
        except:
            pass

# Thread function to process the message queue
def process_messages():
    while server_running:
        sender_socket, message = message_queue.dequeue()
        if message:
            broadcast_message(sender_socket, message)

def main():
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        server_socket.settimeout(1)  # Set timeout for accept to allow checking server_running
        
        print(f"Chat server started on {HOST}:{PORT}")
        print("Waiting for connections...")
        
        # Start message processing thread
        message_thread = threading.Thread(target=process_messages)
        message_thread.daemon = True
        message_thread.start()
        
        # Main loop to accept connections
        while server_running:
            try:
                client_socket, client_address = server_socket.accept()
                client_ip = client_address[0]
                client_port = client_address[1]
                print(f"New connection from {client_ip}:{client_port}")
                
                # Create a new thread to handle this client
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if server_running:
                    print(f"Error accepting connection: {e}")
                    
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Clean up
        try:
            server_socket.close()
        except:
            pass
        print("Server shut down.")

if __name__ == "__main__":
    main()

