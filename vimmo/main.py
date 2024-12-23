import os
from vimmo.API import app

def get_gateway_ip():
    # Run the Docker network inspect command to get the gateway IP
    gateway_ip = os.popen("docker network inspect bridge --format='{{(index .IPAM.Config 0).Gateway}}'").read().strip()
    return gateway_ip

def main():
    gateway_ip = get_gateway_ip()  # Fetch the gateway IP dynamically
    app.run(host=gateway_ip, port=5001, debug=True)

if __name__ == "__main__":
    main()
