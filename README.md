# Django Blog Project

A web application for blogging built with Python and Django framework, featuring Iranian calendar support, tag management, media handling, and PostgreSQL integration.

## Features

- Complete blog post management (CRUD operations)
- Persian date/time display using Jalali calendar
- Article categorization via tagging system
- Automated thumbnail generation for uploaded images
- Markdown support for post content
- User authentication and profile management
- PostgreSQL database support
- Environment variable management for secure deployment

## Tech Stack

- **Python:** 3.14+
- **Framework:** Django 6.0
- **Database:** PostgreSQL
- **Dependencies:**
  - `django-environ`: Environment variable configuration
  - `django-jalali` & `jdatetime`: Jalali datetime support
  - `django-taggit`: Tagging functionality
  - `easy-thumbnails`: Image handling
  - `markdown`: Markdown content processing
  - `psycopg2-binary`: PostgreSQL database adapter
  - `django-debug-toolbar`: Performance debugging tool

## Requirements

Ensure you have Python installed on your system. PostgreSQL is required for database setup.

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/username/django-blog.git
   cd django-blog
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the `MySite/` directory (alongside `manage.py`) with the following variables:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost

   DB_NAME=my_blog
   DB_USER=admin_blog
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=5432

   EMAIL_HOST_USER=your_gmail
   EMAIL_HOST_PASSWORD=your_gmail_app_password
   ```

5. Run database migrations:
   ```bash
   cd MySite
   python manage.py migrate
   ```

6. Create a superuser account:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`.

## Directory Structure

```text
django-blog/
├── MySite/
│   ├── blog/             # Main application
│   ├── MySite/           # Project settings and configuration
│   ├── media/            # User uploaded files
│   ├── static/           # Static assets
│   ├── manage.py         # Django CLI utility
│   └── .env              # Local environment variables
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## License

This project is licensed under the MIT License.
