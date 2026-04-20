# 🌌 Fictional Universe Builder

Fictional Universe Builder is a Django web application for creating and managing fictional universes, characters, stories, and locations. It includes relational validation across connected content, role-based access control, REST API endpoints built with Django REST Framework, and asynchronous email processing with Celery and Redis.

---

## ✨ Features
- **Custom authentication system** with email-based login and user profiles.
- **Automatic profile creation** using Django signals.
- **Role-based access control** with `Members` and `Moderators` groups.
- **Universe management** with genres and descriptive world-building data.
- **Character, story, and location management** with universe-aware relationships and validation.
- **Relational data modeling** using foreign key and many-to-many relationships across universes, genres, stories, characters, and locations.
- **Hierarchical locations** with parent and sub-location relationships.
- **Object-level permissions and relational validation** to ensure content can only be modified by authorized users and related data remains within valid universe boundaries.
- **REST API endpoints** for Universes and Stories using Django REST Framework.
- **Search and sorting** across content collections.
- **Asynchronous welcome emails** using Celery and Redis.

---

## 🛠️ Tech Stack
- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery
- **Broker:** Redis
- **Frontend:** Bootstrap 5, Django Templates, custom CSS
- **Configuration:** `python-dotenv`

---

## 📂 Project Structure
```text
Fictional-Universe-Builder/
├── world_builder/
│   ├── accounts/
│   ├── characters/
│   ├── common/
│   ├── locations/
│   ├── static/
│   ├── stories/
│   ├── templates/
│   ├── universes/
│   ├── world_builder/
│   ├── .env.example
│   ├── manage.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Installation

1. **Clone the repository**

```bash
git clone https://github.com/WExilion/Fictional-Universe-Builder.git
cd Fictional-Universe-Builder/world_builder
```

2. **Create and activate a virtual environment**

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to a new file named `.env`, then fill in the required values.

Then configure:
- Django secret key
- PostgreSQL credentials
- Redis URL
- Email/SMTP credentials

5. **Start Redis**
```bash
redis-server
```

6. **Apply migrations and seed sample data**
```bash
python manage.py migrate
python manage.py seed
```

7. **Start the Django development server**
```bash
python manage.py runserver
```

8. **Start the Celery worker in a separate terminal**

**Windows:**
```bash
celery -A world_builder worker --pool=solo --loglevel=info
```
**macOS / Linux:**
```bash
celery -A world_builder worker --loglevel=info
```

---

## 🧪 Running Tests
The project includes automated tests covering core model behavior, signals, forms, and views.
```bash
python manage.py test
```

---

## 🔐 Environment Variables
| Variable              | Description                   | Default                    |
| --------------------- | ----------------------------- | -------------------------- |
| `SECRET_KEY`          | Django secret key             | -                          |
| `DEBUG`               | Development mode toggle       | `True`                     |
| `ALLOWED_HOSTS`       | Comma-separated allowed hosts | `localhost,127.0.0.1`      |
| `DB_NAME`             | PostgreSQL database name      | -                          |
| `DB_USER`             | PostgreSQL username           | -                          |
| `DB_PASSWORD`         | PostgreSQL password           | -                          |
| `DB_HOST`             | PostgreSQL host               | `127.0.0.1`                |
| `DB_PORT`             | PostgreSQL port               | `5432`                     |
| `REDIS_URL`           | Redis broker URL              | `redis://127.0.0.1:6379/0` |
| `EMAIL_HOST`          | SMTP server host              | -                          |
| `EMAIL_PORT`          | SMTP server port              | -                          |
| `EMAIL_HOST_USER`     | SMTP account username/email   | -                          |
| `EMAIL_HOST_PASSWORD` | SMTP account password         | -                          |
| `EMAIL_USE_TLS`       | Enable TLS for SMTP           | `True`                     |

---

## 🔗 API Endpoints
Authenticated users can create, update, and delete resources based on project permissions.

### Universes API
- `GET /api/universes/` — list universes
- `POST /api/universes/` — create universe
- `GET /api/universes/<slug>/` — retrieve universe details
- `PUT /api/universes/<slug>/` — update universe
- `PATCH /api/universes/<slug>/` — partially update universe
- `DELETE /api/universes/<slug>/` — delete universe

### Stories API
- `GET /api/stories/` — list stories
- `POST /api/stories/` — create story
- `GET /api/stories/<universe_slug>/<slug>/` — retrieve story details
- `PUT /api/stories/<universe_slug>/<slug>/` — update story
- `PATCH /api/stories/<universe_slug>/<slug>/` — partially update story
- `DELETE /api/stories/<universe_slug>/<slug>/` — delete story

---

## 🔗 Main URL Routes

| Page             | URL Pattern                                  |
|------------------|----------------------------------------------|
| Home             | `/`                                          |
| Register         | `/accounts/register/`                        |
| Login            | `/accounts/login/`                           |
| Logout           | `/accounts/logout/`                          |
| Profile Detail   | `/accounts/profile/<pk>/`                    |
| Profile Edit     | `/accounts/profile/edit/`                    |
| Account Delete   | `/accounts/profile/delete/`                  |
| Change Password  | `/accounts/profile/password-change/`         |
| Universes        | `/universes/`                                |
| Universe Create  | `/universes/create/`                         |
| Universe Detail  | `/universes/<slug>/`                         |
| Universe Edit    | `/universes/<slug>/update/`                  |
| Universe Delete  | `/universes/<slug>/delete/`                  |
| Characters       | `/characters/`                               |
| Character Create | `/characters/create/`                        |
| Character Detail | `/characters/<universe_slug>/<slug>/`        |
| Character Edit   | `/characters/<universe_slug>/<slug>/update/` |
| Character Delete | `/characters/<universe_slug>/<slug>/delete/` |
| Locations        | `/locations/`                                |
| Location Create  | `/locations/create/`                         |
| Location Detail  | `/locations/<universe_slug>/<slug>/`         |
| Location Edit    | `/locations/<universe_slug>/<slug>/update/`  |
| Location Delete  | `/locations/<universe_slug>/<slug>/delete/`  |
| Stories          | `/stories/`                                  |
| Story Create     | `/stories/create/`                           |
| Story Detail     | `/stories/<universe_slug>/<slug>/`           |
| Story Edit       | `/stories/<universe_slug>/<slug>/update/`    |
| Story Delete     | `/stories/<universe_slug>/<slug>/delete/`    |

---

## Notes
- Before starting the project, make sure PostgreSQL and Redis are installed and running locally.
- Email functionality depends on valid SMTP credentials.
- Sample data can be loaded with the custom seed management command.

---

*Developed as part of the **Django Advanced** course, within the **Python Web** program.*
