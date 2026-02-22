## Project Overview
A backend service built on Django that gets trading signals through webhooks, processes them, and sends clients updates in real time. 
 - Listens for trading signals sent as plain text to a webhook URL.
 - Parses and validates the signal (BUY/SELL, instrument, SL, TP).
 - Creates an order and simulates execution through a mock broker.
 - Tracks order status (pending → executed → closed).
 - Sends updates to clients in real time.

## Tech Stack
- Python 3.12
- Django 6.0.1
- Django REST Framework 3.16.1
- pydantic 2.12.5
- Celery 5
- Redis
- PostgreSQL
- Channels
- Uvicorn
- Docker


## Set Up Environment Variables
1. Inside the _environment directory, create a `.env` file with the following variables for example or see the .env.example file in the same directory.

```bash
ENVIRONMENT=local
```
2. Inside the same directory, create another file according  to your environment for example `_environment/.env` and add all the variables given in the `.env.example` file. for the assessment purpose, I have commenting out the `_environment/.env` and `_environment/.env.local` files from gitignore. But in the real world, you should have the `_environment/.env` file and the `_environment/.env.local` file in gitignore.

## Project Setup & Installation

This project uses Poetry for dependency management. To set up and run the project locally, follow the steps in readme/POETRY.md.

- Using Poetry – Recommended for managing dependencies and virtual environments easily.
  Follow the steps in readme/POETRY.md for detailed instructions.

**The Simple Steps are given below:**
### Install Poetry on macOS/Linux

Open your terminal. Run the following command to install Poetry:

```zsh
curl -sSL https://install.python-poetry.org | python3 -

```

### 4.2 Add Poetry to your System Path (Linux or Mac):

Add Poetry to your system's `PATH` by adding the following line to your shell configuration file (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):

```zsh
export PATH="$HOME/.local/bin:$PATH"
```

Reload your shell configuration:

```zsh
source ~/.bashrc  # or source ~/.zshrc
```

### Install Dependencies

```zsh
poetry install
```
### Database Setup

```zsh
poetry run python manage.py makemigrations
```

```zsh
poetry run python manage.py migrate
```


### Run the Project

```zsh
poetry run gunicorn config.asgi:application \                                                                                    ─╯
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --worker-connections 1000 \
  --timeout 60 \
  --bind 0.0.0.0:8000

```
### Run Celery Background Workers
```zsh
poetry run celery -A config worker -l info
```
### API Specification

You can explore the full API schema using DRF-Spectacular/OpenAPI. After running the server:

```
http://127.0.0.1:8000/dev/api/docs/

```

Postman Collection
To test the APIs manually, a ready-to-use Postman collection is provided in project directory:

```
Doin Task.json
```

## Test WebSocket

This project includes real-time activity logging using Django Channels and WebSockets. All system-wide events such as order simulates, webhook parsed invalid signals, and order updates are sent to clients in real time.

```bash
    ws://localhost:8000/ws/signals/invalid/
    ws://localhost:8000/ws/orders/
```
## WebSocket Endpoint or Project Team

- Open Postman WebSocket tab, and:

  - Method: WebSocket

  - URL or Project Team Channel:

```bash
    The WebSocket endpoint is:
    ws://localhost:8000/ws/orders/
```
and 
```bash
    ws://localhost:8000/ws/signals/invalid/
```

- Click on the Connect button.

