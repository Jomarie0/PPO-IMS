# PNP Inventory Management System

A comprehensive web-based computer asset and inventory management system for the Philippine National Police (PNP) - Quezon Province.

## System Overview

This system centralizes computer inventory reports from 41 municipal branches into one provincial-level system, replacing the current Excel-based process with a modern Django web application.

## Features

### User Roles
- **Provincial Admin**: Can view ALL branches, generate consolidated reports, view dashboard analytics, manage users
- **Branch Admin**: Can manage their branch inventory, add/edit/update asset records, submit monthly inventory reports
- **Viewer**: View-only access to branch data

### Core Modules
1. **Authentication System**: Login, logout, role-based access control
2. **Branch Management**: 41 municipal branches with user assignments
3. **Asset Management**: Complete CRUD operations with detailed asset tracking
4. **Dashboard Analytics**: Role-based dashboards with Chart.js visualizations
5. **Reporting System**: Monthly, quarterly, and custom reports with PDF/Excel/CSV export
6. **Audit Logging**: Track all asset changes with user and timestamp

## Tech Stack

- **Backend**: Django 5.2.11
- **Frontend**: Django Templates + Bootstrap 5
- **Database**: SQLite3 (development)
- **Charts**: Chart.js
- **PDF Export**: ReportLab
- **Excel Export**: openpyxl

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or extract the project to your desired location**

2. **Create and activate virtual environment**:
   ```bash
   # Navigate to project directory
   cd pnp_inventory_system
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment (Windows)
   venv\Scripts\activate
   
   # Activate virtual environment (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create seed data** (optional but recommended):
   ```bash
   python manage.py seed_data
   ```

6. **Create superuser** (for Django admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main application: http://127.0.0.1:8000/
   - Django admin: http://127.0.0.1:8000/admin/

## 🔑 **Login Credentials**

After running the seed data command, you can use these credentials:

| Role | Username | Password | Access Level | Branch |
|------|----------|----------|-------------|-------|
| Super Admin | `super_admin` | `super123` | Full system control | All branches |
| Provincial Admin | `provincial_admin` | `admin123` | All branches, user management | All branches |
| Main Branch Admin | `main_lucena_admin` | `mainlucena123` | Lucena leadership | Lucena City |
| Branch Admin | `lucena_admin` | `lucena123` | Lucena branch | Lucena City |
| Branch Admin | `tayabas_admin` | `tayabas123` | Tayabas branch | Tayabas City |
| Viewer | `sariaya_viewer` | `sariaya123` | Read-only | Sariaya |

**Note**: The `admin` user (Django superuser) has been updated to Super Admin role.

## 🚀 **How to Run the System**

1. **Navigate to project directory**:
   ```bash
   cd pnp_inventory_system
   ```

2. **Activate virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

3. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the application**:
   - **Main App**: http://127.0.0.1:8000/
   - **Django Admin**: http://127.0.0.1:8000/admin/

## 🛠 **Troubleshooting**

### Common Issues and Solutions

#### 1. TemplateDoesNotExist Error
**Problem**: `TemplateDoesNotExist at / dashboard/dashboard.html`
**Solution**: This was caused by invalid Django template syntax. Fixed by correcting arithmetic operations in templates.

#### 2. HTTP ERROR 405 on Logout
**Problem**: Logout button shows "Method Not Allowed" error
**Solution**: Django logout requires POST method. Fixed by changing logout links to POST forms with CSRF protection.

#### 3. Role-Based Access Issues
**Problem**: Users can't access appropriate pages based on their role
**Solution**: Enhanced RBAC system using Django Groups. Super Admin now has access to user management.

#### 4. Template Syntax Errors
**Problem**: Invalid filter errors like `|div:` and `|mul:`
**Solution**: Django doesn't have arithmetic filters. Use `{% widthratio %}` for percentage calculations.

#### 6. User Management AttributeError
**Problem**: `'UserListView' object has no attribute 'user'`
**Solution**: Fixed by converting function decorators to work properly with class-based views using `@method_decorator`.

#### 7. Asset Creation Branch Field Issue
**Problem**: Branch field shows as required and gets cleared when submitting form
**Solution**: Added hidden field to preserve branch value for users with disabled branch field (branch_admin, viewer). Fixed form validation to handle disabled fields properly.

#### 8. UI/UX Improvements
**Problem**: Interface needs better visual design and confirmation dialogs
**Solution**: Enhanced design with:
- Better muted colors (#6c757d) for improved readability
- Smooth transitions and hover effects on interactive elements
- Professional confirmation modals for critical actions (logout, delete)
- Modern card styling with subtle shadows and animations
- Improved badge styling for status indicators
- Enhanced button interactions with visual feedback

#### 5. Missing User Management Menu
**Problem**: Super Admin couldn't see User Management menu
**Solution**: Updated base template to show User Management for both Super Admin and Provincial Admin.

### Debug Mode
The system includes console printing for debugging. Check the server console for detailed information about:
- User authentication flow
- Role-based routing decisions
- Template rendering process
- Error handling

### Database Issues
If you encounter database problems:
```bash
# Reset database (WARNING: This will delete all data)
python manage.py flush
python manage.py migrate
python manage.py seed_data
```

### Static Files Not Loading
If CSS/JS files don't load:
```bash
python manage.py collectstatic
```

### Port Already in Use
If port 8000 is already in use:
```bash
python manage.py runserver 8001
```

## 📊 **System Features**

### ✅ **Working Features**
- ✅ User authentication with enhanced RBAC
- ✅ Role-based dashboards (Provincial, Branch, Viewer)
- ✅ Asset management (CRUD operations)
- ✅ User management (Super/Provincial Admin)
- ✅ Report generation (PDF, Excel, CSV)
- ✅ Audit logging
- ✅ Confirmation modals for delete actions
- ✅ Responsive Bootstrap 5 UI
- ✅ Chart.js visualizations

### 🔄 **Enhanced RBAC System**
- **Super Admin**: Full system control, user management, all branches
- **Provincial Admin**: All branches, user management, consolidated reports
- **Main Branch Admin**: Branch leadership role, full branch management
- **Branch Admin**: Branch management, asset CRUD, reports
- **Viewer**: Read-only access, reports

### 📱 **User Interface**
- **Modern Design**: Bootstrap 5 with responsive layout
- **Role-Based Navigation**: Dynamic menu based on user role
- **Interactive Charts**: Real-time data visualization
- **Confirmation Modals**: Safe delete operations
- **Professional Styling**: PNP-themed interface

## 🔐 **Security Features**

- **Django Authentication**: Built-in secure authentication
- **CSRF Protection**: All forms include CSRF tokens
- **Role-Based Access**: Enhanced RBAC using Django Groups
- **Audit Logging**: Complete change tracking
- **Session Management**: Secure session handling
- **Input Validation**: Form validation and sanitization

## 📈 **Performance Considerations**

- **Database Optimization**: Efficient queries with select_related
- **Pagination**: Large datasets paginated for performance
- **Static Files**: Optimized CSS and JS delivery
- **Template Caching**: Django template caching enabled
- **Database Indexing**: Proper indexes on frequently queried fields

## Project Structure

```
pnp_inventory_system/
├── config/                 # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                  # User management app
│   ├── models.py          # CustomUser model
│   ├── views.py           # Authentication and user management
│   ├── forms.py           # User forms
│   └── urls.py
├── branches/              # Branch management app
│   ├── models.py          # Branch model
│   ├── management/        # Management commands
│   │   └── commands/
│   │       └── seed_data.py
│   └── urls.py
├── assets/                # Asset management app
│   ├── models.py          # Asset model
│   ├── views.py           # Asset CRUD operations
│   ├── forms.py           # Asset forms
│   └── urls.py
├── dashboard/             # Dashboard app
│   ├── views.py           # Dashboard views
│   └── urls.py
├── reports/               # Reporting app
│   ├── models.py          # Report model
│   ├── views.py           # Report generation
│   └── urls.py
├── audit_logs/            # Audit logging app
│   ├── models.py          # AuditLog model
│   └── urls.py
├── templates/             # HTML templates
│   ├── base.html
│   ├── users/
│   ├── assets/
│   ├── dashboard/
│   └── reports/
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── manage.py
└── requirements.txt
```

## Key Features

### Asset Management
- Complete asset lifecycle tracking
- Property number uniqueness validation
- Status tracking (Active, Under Repair, Missing, Condemned)
- Warranty expiration monitoring
- Personnel assignment

### Dashboard Analytics
- Real-time statistics
- Interactive charts using Chart.js
- Branch comparison (Provincial Admin only)
- Asset type distribution
- Recent activity tracking

### Reporting System
- Monthly inventory reports
- Quarterly summary reports
- Custom date range reports
- Export to PDF, Excel, and CSV formats
- Role-based report access

### Security Features
- Django built-in authentication
- Role-based access control
- Audit logging for all changes
- Secure password hashing

## Usage

### For Provincial Admins
1. Login with provincial admin credentials
2. View overall system dashboard
3. Monitor all branch activities
4. Generate consolidated reports
5. Manage user accounts

### For Branch Admins
1. Login with branch admin credentials
2. View branch-specific dashboard
3. Add, edit, and delete assets
4. Generate branch reports
5. Monitor asset status

### For Viewers
1. Login with viewer credentials
2. View branch assets (read-only)
3. Generate reports
4. Monitor asset status

## Development

### Adding New Branches
1. Access Django admin at /admin/
2. Navigate to Branches section
3. Add new branch with required details
4. Assign users to the branch

### Customizing Reports
1. Modify `reports/views.py` for new report types
2. Update templates in `templates/reports/`
3. Add new URL patterns in `reports/urls.py`

### Extending Asset Fields
1. Update `assets/models.py` Asset model
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Update forms in `assets/forms.py`
4. Update templates as needed

## Production Deployment

For production deployment:

1. **Set DEBUG=False in settings.py**
2. **Configure production database (PostgreSQL recommended)**
3. **Set up static file serving**
4. **Configure HTTPS/SSL**
5. **Set up proper logging**
6. **Configure email settings**
7. **Set up backup procedures**

## Support

For technical support or questions:
- Check Django documentation at https://docs.djangoproject.com/
- Review project code comments
- Contact system administrator

## License

© 2024 Philippine National Police - Quezon Province. All rights reserved.
