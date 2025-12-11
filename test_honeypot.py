import paramiko
import time

def test_ssh_login():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Attempting connection to Honeypot...")
        client.connect('127.0.0.1', port=2222, username='root', password='wrongpassword', timeout=5)
        print("Connected (Unexpected!)")
        client.close()
    except paramiko.AuthenticationException:
        print("Authentication Failed (Expected)")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_ssh_login()
