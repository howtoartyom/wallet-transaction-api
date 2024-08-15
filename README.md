# Wallet Transaction API

## Overview

**Wallet Transaction API** is a robust, scalable Django REST API designed for managing wallets and transactions, adhering to the JSON:API specification. The API supports essential features like pagination, sorting, and filtering, ensuring smooth and efficient management of wallet balances while preventing overdrafts. The backend is powered by MySQL, offering reliability and performance for handling large datasets.

## Features

- **Wallet Management:** Create, update, and manage wallets, each with a unique label and a real-time balance.
- **Transaction Handling:** Record transactions tied to wallets, with automatic balance updates.
- **JSON:API Compliance:** Adheres to the JSON:API specification for standardized API responses.
- **Pagination, Sorting, and Filtering:** Easily paginate, sort, and filter data using built-in Django tools.
- **Error Handling:** Graceful error handling with detailed responses for invalid data submissions.
- **Caching:** Utilizes Redis for caching frequently accessed data to improve performance.
- **Environment-Based Configuration:** Secure management of environment-specific settings via `.env` files.

## JSON:API Plugin Integration

This project integrates the [django-rest-framework-json-api](https://django-rest-framework-json-api.readthedocs.io/en/stable/) plugin to ensure compliance with the JSON:API specification. This plugin standardizes the structure of API responses, making them consistent with the JSON:API format. The plugin is configured in the `settings.py` file, and all serializers and views are adapted to adhere to this format.

## Caching Mechanism

To enhance performance, the API uses Redis as a caching backend. Frequently accessed data, such as wallet balances and recent transactions, are cached to reduce database load and improve response times. The caching mechanism is configured in the `settings.py` file, and specific views or queries are decorated to leverage this caching.

## SQLAlchemy Migrations with Alembic

In addition to Django’s built-in migration system, this project uses Alembic for SQLAlchemy migrations, which offers fine-grained control over database schema changes. Alembic is configured with the `alembic.ini` file, and migrations can be managed using standard Alembic commands. This setup allows for advanced migration scenarios, such as data migrations or complex schema changes that might not be straightforward with Django migrations alone.

## Project Structure

The project follows a modular architecture for ease of development, testing, and maintenance:

```
wallet-transaction-api/
│
├── wallet_transaction_api/
│   ├── migrations/            # Database migrations
│   ├── __init__.py            # Package initializer
│   ├── api_urls.py            # API Urls for Wallet and Transaction
│   ├── models.py              # Data models for Wallet and Transaction
│   ├── serializers.py         # Serializers for transforming models into JSON
│   ├── settings.py            # Django settings module
│   ├── urls.py                # URL routing configuration
│   ├── views.py               # API views for Wallet and Transaction
│   ├── wsgi.py                # WSGI entry-point for deployment
│
├── tests/
│   ├── __init__.py            # Package initializer for tests
│   ├── conftest.py            # Pytest fixtures and configuration
│   ├── test_api.py            # API endpoint tests
│   ├── test_models.py         # Model tests
│
├── .env                       # Environment variables
├── manage.py                  # Django management script
├── README.md                  # Project documentation
├── poetry.lock                # Poetry dependency lock file
├── pyproject.toml             # Poetry configuration
├── Dockerfile                 # Docker configuration for containerization
└── docker-compose.yml         # Docker Compose configuration
```

## Quick Start with Docker

To quickly set up and run the application using Docker, follow these steps:

### 1. Set Up Environment Variables

Create a `.env` file in the root directory of your project and add the following variables:

```bash
SECRET_KEY=your_secret_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
REDIS_URL=redis://localhost:6379/1
```

### 2. Build and Run the Docker Container

```bash
docker-compose up --build
```

The API will be available at `http://127.0.0.1:8000/`.

## Installation

### Prerequisites

- **Python 3.12+**
- **MySQL 5.7+**
- **Poetry** (for dependency management)
- **Redis** (for caching)

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/wallet-transaction-api.git
   cd wallet-transaction-api
   ```

2. **Set Up the Virtual Environment:**

   ```bash
   poetry install
   ```

3. **Configure Environment Variables:**

   Create a `.env` file in the root directory and add the following variables:

   ```bash
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   DATABASE_URL=mysql://<db_user>:<db_password>@localhost:3306/<db_name>
   DB_NAME=wallet_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   REDIS_URL=redis://localhost:6379/1
   ```

4. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://127.0.0.1:8000/`.

## Usage

### API Endpoints

- **Wallets:**
  - `GET /api/wallets/` - List all wallets
  - `POST /api/wallets/` - Create a new wallet
  - `GET /api/wallets/{id}/` - Retrieve a wallet by ID
  - `PATCH /api/wallets/{id}/` - Update a wallet
  - `DELETE /api/wallets/{id}/` - Delete a wallet

- **Transactions:**
  - `GET /api/transactions/` - List all transactions
  - `POST /api/transactions/` - Create a new transaction
  - `GET /api/transactions/{id}/` - Retrieve a transaction by ID
  - `PATCH /api/transactions/{id}/` - Update a transaction
  - `DELETE /api/transactions/{id}/` - Delete a transaction

### Example Request

**Creating a Wallet:**

```bash
curl -X POST http://127.0.0.1:8000/api/wallets/ \
-H "Content-Type: application/vnd.api+json" \
-d '{
    "data": {
        "type": "Wallet",
        "attributes": {
            "label": "My Wallet",
            "balance": "100.00"
        }
    }
}'
```

**Creating a Transaction:**

```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
-H "Content-Type: application/vnd.api+json" \
-d '{
    "data": {
        "type": "Transaction",
        "attributes": {
            "txid": "TX123",
            "amount": "50.00",
            "wallet": "1"
        }
    }
}'
```

## Running Tests

To run the test suite with coverage:

```bash
pytest --cov=wallet_transaction_api
```

## Deployment

To deploy the API, ensure your production settings are configured in `settings.py`, particularly the `DEBUG`, `ALLOWED_HOSTS`, and database settings. You may use Docker for containerization or deploy on platforms like AWS, Heroku, or DigitalOcean.


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
