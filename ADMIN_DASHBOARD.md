# Admin Dashboard Documentation

## Overview
The enhanced admin dashboard provides comprehensive management tools for administrators to manage lost & found items, users, and system statistics.

## Features

### 1. **Manage Requests & Items Tab**
View, filter, edit, and delete all lost & found items in the system.

#### Capabilities:
- **View All Items**: Display items in a card grid layout with full details
- **Filter Items**: Filter by status or category:
  - All
  - Lost
  - Found  
  - Resolved
  - Pending (Yet to be found)
- **Edit Items**: Modify item details (title, description, category, status)
- **Delete Items**: Permanently remove items from the database
- **Mark Resolved**: Quickly mark items as resolved
- **View Images**: See uploaded item images with proper formatting

#### Actions:
- 🔵 **Edit**: Open edit modal to modify item details
- 🔴 **Delete**: Remove item permanently (with confirmation)
- 🟢 **Mark Resolved**: Update item status to resolved

---

### 2. **Manage Users Tab**
View and manage all registered users and administrators in the system.

#### Capabilities:
- **View All Users**: Display users in a table format with their roles
- **Delete Users**: Remove users from the system
- **View User Roles**: Distinguish between students and admins with color-coded badges

#### User Roles:
- **Student**: Regular users who can report lost/found items
- **Admin**: Administrative users with full dashboard access

#### Actions:
- 🔴 **Delete**: Remove user from system (with confirmation)

---

### 3. **Add Item Tab**
Create new lost & found item reports directly from the admin dashboard.

#### Fields:
- **Title**: Item name (e.g., "Black Laptop Backpack")
- **Description**: Detailed item description
- **Category**: Select from:
  - Electronics
  - Books
  - Accessories
  - Documents
  - Other
- **Location**: Where the item was found/lost
- **Phone**: Contact number for the report
- **Image**: Optional image upload for visual identification

#### Process:
1. Fill in all required fields
2. Upload image (optional)
3. Click "Add Item"
4. Dashboard automatically reloads with new item

---

### 4. **Add User Tab**
Create new user accounts for students and administrators.

#### Fields:
- **Student ID**: Unique identifier (e.g., "S12345", "admin01")
- **Passcode**: Password for login
- **Role**: Select from:
  - Student
  - Admin

#### Process:
1. Enter student ID (must be unique)
2. Create a passcode
3. Select user role
4. Click "Add User"
5. System validates and creates account

#### Validation:
- Student ID must be unique
- Role must be either 'student' or 'admin'

---

### 5. **Statistics Tab**
View real-time statistics about items and users in the system.

#### Metrics Displayed:
- **Total Items**: Count of all items in database
- **Lost Items**: Count of items marked as "Lost"
- **Found Items**: Count of items marked as "Found"
- **Resolved**: Count of resolved items
- **Total Users**: Count of all registered users (students only)
- **Total Admins**: Count of administrator accounts

#### Visualization:
- Color-coded stat cards:
  - 🔵 Blue: Total Items
  - 🔴 Red: Lost Items
  - 🟢 Green: Found Items
  - 🟣 Purple: Resolved Items

---

## API Endpoints

### Item Management
```
POST   /add-item                           - Create new item
GET    /items                              - List all items
POST   /update-item/{item_id}              - Update item details
DELETE /delete-item/{item_id}              - Delete item
POST   /update-item-status/{item_id}       - Update item status
POST   /mark-resolved/{item_id}            - Mark item as resolved
```

### User Management
```
GET    /get-users                          - Fetch all users
POST   /add-user                           - Create new user
DELETE /delete-user/{user_id}              - Delete user
```

### Admin Routes
```
GET    /api/admin/users                    - Get all users (with pagination support)
POST   /api/admin/add-user                 - Add user via API
DELETE /api/admin/delete-user/{user_id}    - Delete user via API
POST   /api/admin/update-user/{user_id}    - Update user details
POST   /api/admin/update-item-status/{item_id} - Update item status
GET    /api/admin/item-stats               - Get dashboard statistics
```

---

## User Interface

### Header
- Application title with cog icon
- Logout button (top right)

### Tab Navigation
- Smooth tab switching without page reload
- Active tab highlighted in blue
- All tabs accessible from single dashboard view

### Item Cards
- **Card Layout**: Responsive grid (1 column on mobile, 2 on tablet, 3 on desktop)
- **Information**: Title, description, category, location, phone, status
- **Status Badge**: Color-coded based on item status
- **Image Display**: Optional item image with 160px height and cover fit
- **Action Buttons**: Edit, Delete, Mark Resolved

### Modals
- **Edit Item Modal**: Full form for modifying item details
- **Delete Confirmation Modal**: Confirmation before user deletion
- **Outside Click Close**: Click outside modal to close

---

## Database Schema

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    phone TEXT NOT NULL,
    image_path TEXT,
    embedding TEXT,
    status TEXT DEFAULT 'Yet to be found'
)
```

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    passcode TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin')) NOT NULL
)
```

---

## Status Codes

### Item Status Values
- **Yet to be found**: Default status for new items
- **Lost**: Item is confirmed lost
- **Found**: Item is confirmed found
- **Resolved**: Item has been resolved (matched/returned)

---

## Error Handling

- **Invalid Item ID**: Returns 404 Not Found
- **Invalid Status**: Returns 400 Bad Request
- **Duplicate Student ID**: Returns 400 Bad Request when adding user
- **Invalid Role**: Returns 400 Bad Request if role is not 'student' or 'admin'
- **Database Errors**: Returns 500 Internal Server Error

---

## Features Implemented

✅ Complete CRUD for items (Create, Read, Update, Delete)
✅ Complete CRUD for users (Create, Read, Delete)
✅ Real-time statistics dashboard
✅ Item filtering by status and category
✅ Item status management
✅ User role management
✅ Image support for items
✅ Responsive design for all screen sizes
✅ Modal forms for better UX
✅ Confirmation dialogs for destructive actions
✅ Color-coded status badges
✅ Tab-based navigation

---

## How to Use

### Login as Admin
1. Go to login page
2. Enter admin credentials:
   - Student ID: `admin01`
   - Passcode: `adminpass`
3. You will be redirected to the admin dashboard

### Add a New Item
1. Click "Add Item" tab
2. Fill in all required fields
3. Upload an image (optional)
4. Click "Add Item"

### Add a New User
1. Click "Add User" tab
2. Enter Student ID (must be unique)
3. Set Passcode
4. Select role (Student or Admin)
5. Click "Add User"

### Manage Items
1. View items in "Manage Requests" tab
2. Use filter buttons to narrow down items
3. Click "Edit" to modify item details
4. Click "Delete" to remove item
5. Click "Mark Resolved" to update status

### View Statistics
1. Click "Statistics" tab
2. View real-time counts and metrics
3. Statistics update automatically when items/users are added/modified

---

## Technology Stack

- **Frontend**: HTML5, CSS3 (Tailwind CSS), JavaScript (Vanilla)
- **Backend**: FastAPI, SQLite3
- **Icons**: Font Awesome 6.0
- **Styling**: Tailwind CSS 2.2.19

---

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## Future Enhancements

- [ ] Export statistics to CSV/PDF
- [ ] Advanced search with date range filters
- [ ] Bulk operations (bulk delete, bulk status update)
- [ ] User activity logs
- [ ] Admin action audit trail
- [ ] Email notifications for item matches
- [ ] Dashboard customization options
- [ ] Dark mode theme
- [ ] Multi-language support

---

## Troubleshooting

### Items not loading
- Ensure database is initialized
- Check if database file exists at configured path
- Verify UPLOAD_DIR path in config

### Modals not closing
- Try clicking outside the modal
- Refresh the page and try again
- Check browser console for JavaScript errors

### User creation fails
- Verify Student ID is unique
- Check if role is 'student' or 'admin'
- Ensure all required fields are filled

### Images not displaying
- Verify image was uploaded successfully
- Check UPLOAD_DIR permissions
- Ensure image file exists in uploads directory

---

## Contact & Support

For issues or feature requests related to the admin dashboard, please contact the development team.
