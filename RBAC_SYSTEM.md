# Enhanced RBAC System for PNP Inventory Management

## Overview
The system now uses Django Groups for enhanced Role-Based Access Control (RBAC) with a hierarchical structure designed specifically for the PNP organizational structure.

## User Roles and Hierarchy

### 1. Super Admin
- **Purpose**: System administrator with full control
- **Permissions**: 
  - Can manage all branches
  - Can manage all users (including Super Admins)
  - Can create, edit, delete all assets
  - Can access all system features
- **Branch Assignment**: Not required
- **Django Group**: Super Admins

### 2. Provincial Admin
- **Purpose**: Provincial-level management
- **Permissions**:
  - Can view ALL branches
  - Can generate consolidated reports
  - Can view dashboard analytics
  - Can manage users (except Super Admins)
  - Can create, edit, delete all assets
- **Branch Assignment**: Not required
- **Django Group**: Provincial Admins

### 3. Main Branch Admin
- **Purpose**: Main branch leadership (e.g., Provincial HQ)
- **Permissions**:
  - Can manage their branch inventory
  - Can add/edit/update asset records
  - Can submit monthly inventory report
  - Can generate branch reports
  - Can create and edit assets
- **Branch Assignment**: Required
- **Django Group**: Main Branch Admins

### 4. Branch Admin
- **Purpose**: Regular branch management
- **Permissions**:
  - Can manage their branch inventory
  - Can add/edit/update asset records
  - Can submit monthly inventory report
  - Can generate branch reports
  - Can create and edit assets
- **Branch Assignment**: Required
- **Django Group**: Branch Admins

### 5. Viewer
- **Purpose**: Read-only access
- **Permissions**:
  - View-only access to branch data
  - Can generate reports
  - Can view dashboard analytics
  - Cannot modify any data
- **Branch Assignment**: Required
- **Django Group**: Viewers

## Django Groups Structure

The system automatically creates and manages these Django Groups:

- **Super Admins**: Full system access
- **Provincial Admins**: Provincial-level management
- **Main Branch Admins**: Main branch leadership
- **Branch Admins**: Regular branch management
- **Viewers**: Read-only access

## Permission Matrix

| Action | Super Admin | Provincial Admin | Main Branch Admin | Branch Admin | Viewer |
|--------|-------------|------------------|-------------------|-------------|--------|
| View All Branches | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Assets | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit Assets | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete Assets | ✅ | ✅ | ❌ | ❌ | ❌ |
| Generate Reports | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |

## Implementation Features

### Automatic Group Assignment
When a user is created or updated, the system automatically:
1. Removes the user from all role-based groups
2. Assigns the user to the appropriate group based on their role
3. Ensures group membership is always synchronized with the role field

### Enhanced Permission Checking
The system uses property methods for clean permission checking:
- `user.can_manage_all_branches`
- `user.can_manage_users`
- `user.can_create_assets`
- `user.can_edit_assets`
- `user.can_delete_assets`
- `user.can_view_all_assets`

### Branch Access Control
- Users with `can_view_all_assets` can see all branches
- Other users can only see their assigned branch
- Automatic filtering in views based on user permissions

## Default Accounts

The system includes these pre-configured accounts:

| Username | Role | Password | Branch | Purpose |
|----------|------|----------|---------|---------|
| super_admin | Super Admin | super123 | None | System administration |
| provincial_admin | Provincial Admin | admin123 | None | Provincial management |
| main_lucena_admin | Main Branch Admin | mainlucena123 | Lucena City | Main branch leadership |
| lucena_admin | Branch Admin | lucena123 | Lucena City | Regular branch admin |
| tayabas_admin | Branch Admin | tayabas123 | Tayabas City | Regular branch admin |
| sariaya_viewer | Viewer | sariaya123 | Sariaya | Read-only access |

## Django Admin Integration

The Django Admin interface is enhanced with:
- Custom user admin interface
- Role-based filtering
- Branch assignment display
- Group management capabilities

## Security Benefits

1. **Hierarchical Access**: Clear separation of duties and responsibilities
2. **Group-Based Permissions**: Leverages Django's built-in security features
3. **Automatic Synchronization**: Groups are always synchronized with user roles
4. **Branch Isolation**: Users can only access their assigned data
5. **Audit Trail**: All actions are logged with user information

## Usage in Django Admin

1. Navigate to `/admin/`
2. Go to "Users" section
3. Create or edit users
4. Assign roles and branches
5. Groups are automatically managed

## Future Enhancements

The system is designed to be easily extensible:
- Add new roles by updating ROLE_CHOICES
- Create custom permissions as needed
- Implement branch-level permissions
- Add time-based access controls

This RBAC system provides a robust, scalable foundation for the PNP Inventory Management System with proper security controls and organizational hierarchy.
