# Makefile for FTP Server and Client

# Variables
SERVER = server.py
CLIENT = client.py
SERVER_LOG = server.log
CERT_FILE = server.crt
KEY_FILE = server.key
ID_PASSWD_FILE = id_passwd.txt
STORAGE_ROOT = server_storage

# Default target: build and run the server
all: run_server

# Run server
run_server:
	@echo "Starting FTP Server..."
	python3 $(SERVER)

# Run client
run_client:
	@echo "Starting FTP Client..."
	python3 $(CLIENT)

# Run server with SSL
run_server_ssl:
	@echo "Starting FTP Server with SSL..."
	python3 $(SERVER) --ssl

# Clean logs and server storage
clean:
	@echo "Cleaning up server logs and storage..."
	rm -f $(SERVER_LOG)
	rm -rf $(STORAGE_ROOT)

# Generate server certificates (if needed)
generate_certs:
	@echo "Generating self-signed certificates..."
	openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
		-keyout $(KEY_FILE) -out $(CERT_FILE) \
		-subj "/C=US/ST=California/L=San Francisco/O=MyOrg/OU=Dev/CN=localhost"

# Check for missing files
check_files:
	@echo "Checking for necessary files..."
	@if [ ! -f $(CERT_FILE) ]; then echo "Certificate file $(CERT_FILE) not found!"; fi
	@if [ ! -f $(KEY_FILE) ]; then echo "Key file $(KEY_FILE) not found!"; fi
	@if [ ! -f $(ID_PASSWD_FILE) ]; then echo "Password file $(ID_PASSWD_FILE) not found!"; fi
	@if [ ! -d $(STORAGE_ROOT) ]; then echo "Storage directory $(STORAGE_ROOT) not found!"; fi

# Help section
help:
	@echo "Makefile options:"
	@echo "  make run_server      Start the FTP server"
	@echo "  make run_client      Start the FTP client"
	@echo "  make clean           Clean server logs and storage"
	@echo "  make generate_certs  Generate self-signed SSL certificates"
	@echo "  make check_files     Check for necessary files"
