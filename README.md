# Opportunity Tracker

## Project Description

Opportunity Tracker is a tool designed to help users manage and track business opportunities efficiently. It provides features such as opportunity creation, status tracking, and reporting to streamline workflows and improve productivity.

## Features

- Create and manage opportunities.
- Track the status of opportunities in real-time.
- Generate detailed reports for analysis.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hirensoni913/opportunity_tracker.git
   ```
2. Navigate to the project directory:
   ```bash
   cd opportunity_tracker
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Rename the `.env.example` file to `.env`:
   ```bash
   mv .env.example .env  # On Windows: rename .env.example .env
   ```
6. Update the `.env` file with your configuration values.

7. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

## Environment Variables

Below is a table explaining the environment variables used in the project:

| Variable Name                   | Description                                               |
| ------------------------------- | --------------------------------------------------------- |
| `SITE_URL`                      | The base URL of the site.                                 |
| `DEBUG`                         | Set to `True` for development and `False` for production. |
| `DJANGO_ALLOWED_HOSTS`          | Comma-separated list of allowed hosts.                    |
| `DJANGO_SECRET_KEY`             | The secret key for Django.                                |
| `DJANGO_CSRF_TRUSTED_ORIGIN`    | Trusted origin for CSRF protection.                       |
| `DB_ENGINE`                     | Database engine (e.g., `django.db.backends.postgresql`).  |
| `DB_HOST`                       | Database host.                                            |
| `DB_PORT`                       | Database port.                                            |
| `DB_USER`                       | Database username.                                        |
| `DB_PWD`                        | Database password.                                        |
| `DB_NAME`                       | Database name.                                            |
| `CELERY_BROKER_URL`             | URL for the Celery broker (e.g., Redis).                  |
| `EMAIL_BACKEND`                 | Email backend to use (e.g., SMTP).                        |
| `EMAIL_HOST`                    | SMTP server host.                                         |
| `EMAIL_PORT`                    | SMTP server port.                                         |
| `EMAIL_USE_TLS`                 | Whether to use TLS for email.                             |
| `EMAIL_HOST_USER`               | SMTP username.                                            |
| `EMAIL_HOST_PASSWORD`           | SMTP password.                                            |
| `DEFAULT_FROM_EMAIL`            | Default "from" email address.                             |
| `NEW_OPPORTUNITY_ALERT_CHANNEL` | Notification channel for new opportunities.               |
| `APP_ID`                        | WhatsApp application ID.                                  |
| `VERSION`                       | API version for WhatsApp integration.                     |
| `APP_SECRET`                    | Application secret for WhatsApp.                          |
| `RECIPIENT_WAID`                | WhatsApp recipient ID.                                    |
| `PHONE_NUMBER_ID`               | WhatsApp phone number ID.                                 |
| `ACCESS_TOKEN`                  | Access token for WhatsApp API.                            |

## Usage

1. Start the development server:
   ```bash
   python manage.py runserver
   ```
2. Open your browser and navigate to `http://127.0.0.1:8000`.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the GNU General Public License v3. See the `LICENSE` file for details.
