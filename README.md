# School Timetable Management System

A comprehensive Django-based web application for managing and displaying school timetables. Features both REST API endpoints and modern web interfaces with grid and list views for easy schedule visualization.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2+-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14+-orange.svg)

---

## ✨ Features

### Frontend Interface

- **Grid View**: Excel-like timetable layout with visual distinction between lectures and practice sessions
  - Separate columns for each student group
  - Lectures displayed as merged cells across all groups
  - Practice sessions shown in individual group columns
  - Color-coded cells (blue for lectures, orange for practice)
  - Responsive design with print support
- **List View**: Detailed table format with comprehensive filtering options
  - Filter by faculty, course, group, teacher, week, and day
  - Sortable columns
  - Responsive Bootstrap-based design

### REST API

- Full CRUD operations for timetable management
- Advanced filtering and search capabilities
- Swagger/OpenAPI documentation
- CORS-enabled for frontend integration
- Optimized database queries with `select_related`

### Data Models

- Faculties and Courses
- Student Groups
- Teachers and Subjects
- Lesson Types (Lecture/Practice)
- Weeks and Days
- Lesson Numbers with time slots
- Timetable Entries

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/DovletEmin/Schedule.git
cd Schedule
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply database migrations**

```bash
cd src
python manage.py migrate
```

5. **Create superuser (for admin access)**

```bash
python manage.py createsuperuser
```

6. **Run development server**

```bash
python manage.py runserver
```

7. **Access the application**

- Main Grid View: http://localhost:8000/
- List View: http://localhost:8000/list/
- Admin Panel: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/docs/

---

## 📡 API Endpoints

### Timetable Queries

**Get schedule for specific week and day**

```http
GET /api/<week_number>/<day_number>/
```

Example: `/api/1/2/` - Returns schedule for week 1, day 2

**Get full week schedule**

```http
GET /api/<week_number>/
```

Example: `/api/1/` - Returns all schedule entries for week 1

**Advanced search with filters**

```http
GET /api/search/?teacher=<name>&week=<num>&day=<num>&group=<name>
```

**Available query parameters:**

- `teacher` - Filter by teacher name (partial match)
- `week` - Filter by week number
- `day` - Filter by day number
- `group` - Filter by group name (partial match)
- `faculty` - Filter by faculty name (partial match)
- `course` - Filter by course number
- `lesson_number` - Filter by lesson number

### API Documentation

**Swagger UI**: http://localhost:8000/api/docs/  
**ReDoc**: http://localhost:8000/api/redoc/  
**OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🎨 Frontend Features

### Grid View

The main timetable view displays schedules in a grid format similar to Excel:

- **Header**: Shows student group names across columns
- **Rows**: Organized by days (vertical) and lesson numbers
- **Lectures**: Displayed as merged cells spanning all groups with:
  - Blue gradient background
  - Subject name and teacher
  - Room number in separate column
- **Practice Sessions**: Individual cells for each group with:
  - Orange background
  - Subject name and teacher
  - Room number in separate column

**Filters:**

- Faculty (optional)
- Week (optional)
- Displays all courses automatically

### List View

Detailed table format with comprehensive information:

- All timetable entries in tabular format
- Advanced filtering by multiple parameters
- Sortable columns
- Responsive design for mobile devices

---

## 🗂️ Project Structure

```
Schedule/
├── src/
│   ├── src/                      # Django project settings
│   │   ├── settings.py          # Main settings
│   │   ├── urls.py              # Root URL configuration
│   │   └── wsgi.py              # WSGI configuration
│   │
│   ├── timetable/               # Main application
│   │   ├── models.py            # Data models
│   │   ├── views.py             # Frontend and API views
│   │   ├── serializers.py       # DRF serializers
│   │   ├── filters.py           # QuerySet filters
│   │   ├── admin.py             # Admin panel configuration
│   │   ├── urls.py              # App URL patterns
│   │   │
│   │   ├── templates/           # HTML templates
│   │   │   ├── base.html        # Base template
│   │   │   ├── timetable_grid.html   # Grid view
│   │   │   └── timetable.html   # List view
│   │   │
│   │   ├── templatetags/        # Custom template filters
│   │   │   └── timetable_filters.py
│   │   │
│   │   ├── migrations/          # Database migrations
│   │   └── tests/               # Unit tests
│   │
│   ├── static/
│   │   └── css/
│   │       └── style.css        # Custom styles
│   │
│   ├── manage.py                # Django management script
│   └── db.sqlite3               # SQLite database
│
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

---

## 🛠️ Technologies Used

- **Backend**: Django 5.2.7, Django REST Framework
- **Database**: SQLite (development), PostgreSQL-ready
- **Frontend**: Bootstrap 5.3, HTML5, CSS3
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)
- **CORS**: django-cors-headers
- **Filtering**: django-filter

---

## 📋 Admin Panel

Access at `/admin/` with superuser credentials.

**Features:**

- Manage all entities (Faculties, Courses, Groups, Teachers, etc.)
- Bulk operations and inline editing
- Search and filter capabilities
- User-friendly interface for timetable entry management

---

## 🔧 Configuration

### CORS Settings

Configure allowed origins in `src/src/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Static Files

Static files are configured to be served from `src/static/` directory.

To collect static files for production:

```bash
python manage.py collectstatic
```

---

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

Or with Django's test runner:

```bash
python manage.py test
```

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Dovlet Eminov**

- Email: dovlet.eminov26.02@gmail.com
- GitHub: [@DovletEmin](https://github.com/DovletEmin)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📸 Screenshots

### Grid View

Beautiful Excel-like timetable with color-coded lectures and practice sessions, organized by student groups.

### List View

Comprehensive table format with advanced filtering options for detailed schedule browsing.

---

## 🔄 Recent Updates

- ✅ Added comprehensive grid view with separate columns for each group
- ✅ Implemented lecture/practice visual distinction
- ✅ Added custom CSS styling with responsive design
- ✅ Created template filters for dynamic rendering
- ✅ Improved navigation between grid and list views
- ✅ Enhanced print support for timetables

---

**Made with ❤️ for educational institutions**
