# AURA Honeypot

**Version:** 1.0

AURA Honeypot is a research-oriented SSH honeypot setup using Cowrie and HAProxy for monitoring and logging unauthorized SSH attempts. This project provides a controlled environment to study attacker behavior and capture threat data.

---

## Features (Version 1.0)

- Multiple honeypot instances (`cowrie_a`, `cowrie_b`) with separate profiles
- HAProxy-based SSH proxy for external access
- Logging of SSH attempts into structured JSON/JSONL format
- User database configuration for testing authentication
- Controller module to manage honeypot operations
- Easy volume-based separation of logs and configuration for portability

---

## Next Steps / Roadmap

- Correct login configuration for testing authorized users
- Integration with alerting or visualization tools
- Support for additional protocols beyond SSH
- Enhance userdb management with more flexible credentials

---

## Submodules

The project includes:

- **controller/** – Python-based controller scripts
- **profiles/** – Cowrie profiles for different honeypot instances
- **haproxy/** – HAProxy configuration files
- **cowrie-data/** (ignored in Git) – Runtime data
- **cowrie-logs/** (ignored in Git) – Honeypot logs

---

## Installation Guide

### Prerequisites

- Ubuntu or compatible Linux distribution
- Docker & Docker Compose installed
- Git installed

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/abinrajmk8/aura_honeypot.git
    cd aura_honeypot
    ```

2. Build and start containers:

    ```bash
    sudo docker-compose up -d
    ```

3. Confirm containers are running:

    ```bash
    sudo docker ps
    ```

4. (Optional) Tail honeypot logs:

    ```bash
    tail -f profiles/profile_a/log/cowrie.log
    ```

---

## Setup and Usage

### Profiles Configuration

Each profile folder (`profile_a`, `profile_b`) contains:

- `etc/cowrie.cfg` – Cowrie configuration
- `etc/userdb.txt` – Users and passwords

### Controller

Manage honeypot actions via `controller/controller.py`. Example:

```bash

python3 controller/controller.py

```

### HAProxy

HAProxy listens on port 2222 and routes connections to Cowrie containers.

### Git Ignore

Logs and runtime data are ignored by Git. `.gitignore` includes:

```bash
profiles/*/log/
profiles/*/lib/
cowrie-data/
*.pyc
__pycache__/
*.swp
.DS_Store
```

###Notes

- Default login attempts are denied until userdb.txt and permissions are corrected.

- All captured attempts are stored in JSON/JSONL format (cowrie_events.jsonl).

- Version 1.0; future releases will include proper login support and advanced analytics.

Author: Abin Raj MK
GitHub: https://github.com/abinrajmk8/aura_honeypot
