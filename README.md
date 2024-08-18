# Horsing Around

Horsing Around is a web application designed to help volunteers in a horse farm track chores for each horse. It provides a user-friendly interface to manage horses and their associated tasks, with separate access for administrators and volunteers.

## Features

- Welcome screen with information about the benefits of volunteering in a horse ranch
- Separate access for administrators and volunteers
- Display a grid of horses with their names and pictures
- Show horse information on hover
- Track chores for each horse with checkboxes
- Chores are categorized into Day Opening, Pre Lesson, Post Lesson, and End of Day
- Add new horses to the system (admin only)
- Add new chores to the system (admin only)
- Remove horses and chores (admin only)
- Change admin password
- Automatic reset of checkboxes at midnight
- Responsive design using Bootstrap

## Prerequisites

- Docker
- Docker Compose

## Installation and Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/horsing-around.git
   cd horsing-around
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

3. Access the application in your web browser at `http://localhost:5000`

## Usage

- Welcome Page: The main page displays information about volunteering and options to continue as a volunteer or log in as an admin.
- Volunteer Access: Click on "Continue as Volunteer" to view horses and chores. Volunteers can mark chores as completed.
- Admin Access: 
  - Default credentials: username: `admin`, password: `admin`
  - Admins can add/remove horses and chores, and change their password
- View horses: The main page displays a grid of horses with their names and pictures.
- View horse info: Hover over a horse card to see additional information about the horse.
- Track chores: Each horse card has a list of chores categorized by time of day. Check the boxes to mark chores as completed.
- Add a new horse (Admin): Use the "Add New Horse" form at the bottom of the page to add a new horse to the system.
- Add a new chore (Admin): Use the "Add New Chore" form at the bottom of the page to add a new chore to the system.
- Remove a horse or chore (Admin): Use the remove buttons next to each horse or chore.
- Change password (Admin): Use the "Change Password" form at the bottom of the page.

## File Structure

```
horsing-around/
├── app.py
├── templates/
│   ├── index.html
│   ├── welcome.html
│   └── login.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Customization

- To add custom graphics, place your image files in the `static/images/` directory and update the image URLs in the MongoDB database or the add horse form.
- To modify the styling, edit the `static/css/style.css` file.
- To change the functionality, modify the `app.py` and `static/js/main.js` files.

## Contributing

Feel free to fork this repository and submit pull requests to contribute to this project.

## License

This project is licensed under the MIT License.