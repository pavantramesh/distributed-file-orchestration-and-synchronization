import socket
import ssl
import json
import os
from pathlib import Path

class FileTransferClient:
    def __init__(self, host='localhost', port=9999, certfile='server.crt'):
        self.host = host
        self.port = port
        self.socket = None
        self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.ssl_context.load_verify_locations(certfile)

    def connect(self, username, password):
        """Connect to server and authenticate"""
        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = self.ssl_context.wrap_socket(raw_socket, server_hostname=self.host)
            self.socket.connect((self.host, self.port))
            
            # Send authentication data
            auth_data = {'username': username, 'password': password}
            self.socket.send(json.dumps(auth_data).encode())
            
            # Receive authentication response
            response = self._receive_data()
            if response and response.get('status') == 'success':
                return True
            else:
                print("Authentication failed.")
                return False
        except (socket.error, ssl.SSLError, json.JSONDecodeError) as e:
            print(f"Connection error: {e}")
            return False
    
    def _receive_data(self):
        """Helper function to receive data from the server."""
        try:
            data = self.socket.recv(4096)
            while data:
                try:
                    return json.loads(data.decode())
                    print("Received from server:", response) 
                except json.JSONDecodeError:
                    data += self.socket.recv(4096)
            return None
        except socket.error as e:
            print(f"Data reception error: {e}")
            return None

    def list_files(self):
        """List files in user's directory"""
        self.socket.send(json.dumps({'command': 'list'}).encode())
        response = self._receive_data()
        return response.get('files', []) if response and response.get('status') == 'success' else []
    
    def upload_file(self, filepath):
        """Upload a file to the server"""
        if not os.path.exists(filepath):
            print("File not found.")
            return False
        
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        # Send upload command
        self.socket.send(json.dumps({
            'command': 'upload',
            'filename': filename,
            'size': file_size
        }).encode())
        
        # Send file data
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                self.socket.sendall(chunk)
        
        response = self._receive_data()
        return response.get('status') == 'success' if response else False
    
    def download_file(self, filename, save_path):
        """Download a file from the server"""
        self.socket.send(json.dumps({
            'command': 'download',
            'filename': filename
        }).encode())
        
        response = self._receive_data()
        if response and response.get('status') == 'success':
            file_size = response['size']
            save_path = Path(save_path) / filename
            
            with open(save_path, 'wb') as f:
                received = 0
                while received < file_size:
                    chunk = self.socket.recv(min(4096, file_size - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            return True
        else:
            print("Download failed or file not found on server.")
            return False
    
    def view_file(self, filename):
        """View first 1024 bytes of a file"""
        self.socket.send(json.dumps({
            'command': 'view',
            'filename': filename
        }).encode())
        
        response = self._receive_data()
        return response.get('preview') if response and response.get('status') == 'success' else None
    
    def delete_file(self, filename):
        """Delete a file from the server"""
        self.socket.send(json.dumps({
            'command': 'delete',
            'filename': filename
        }).encode())
        
        response = self._receive_data()
        return response.get('status') == 'success' if response else False
    
    def close(self):
        """Close the connection"""
        if self.socket:
            try:
                self.socket.close()
                print("Connection closed.")
            except socket.error as e:
                print(f"Error closing connection: {e}")

def main():
    client = FileTransferClient()
    
    try:
        # Get credentials
        username = input("Username: ")
        password = input("Password: ")
        
        # Connect and authenticate
        if not client.connect(username, password):
            return
        
        print("Connected to server!")
        
        while True:
            print("\nAvailable commands:")
            print("1. List files")
            print("2. Upload file")
            print("3. Download file")
            print("4. View file")
            print("5. Delete file")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ")
            
            if choice == '1':
                files = client.list_files()
                print("\nFiles in your directory:")
                for file in files:
                    print(f"- {file}")
            
            elif choice == '2':
                filepath = input("Enter file path to upload: ")
                if client.upload_file(filepath):
                    print("File uploaded successfully.")
                else:
                    print("Upload failed.")
            
            elif choice == '3':
                filename = input("Enter filename to download: ")
                save_path = input("Enter directory to save file: ")
                if client.download_file(filename, save_path):
                    print("File downloaded successfully.")
                else:
                    print("Download failed.")
            
            elif choice == '4':
                filename = input("Enter filename to view: ")
                preview = client.view_file(filename)
                if preview:
                    print("\nFile preview:")
                    print(preview)
                else:
                    print("Failed to view file.")
            
            elif choice == '5':
                filename = input("Enter filename to delete: ")
                if client.delete_file(filename):
                    print("File deleted successfully.")
                else:
                    print("Delete failed.")
            
            elif choice == '6':
                break
            
            else:
                print("Invalid choice.")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.close()

if __name__ == '__main__':
    main()
