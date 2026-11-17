# 🔍 Smart Lost & Found System

<p align="center">
  A Web-Based Platform to Report, Search, Match and Recover Lost Items.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JS-orange" alt="Frontend">
  <img src="https://img.shields.io/badge/Status-Completed-success" alt="Status">
</p>

---

## 📌 Table of Contents

1. [About the Project](#-about-the-project)
2. [Problem Statement](#-problem-statement)
3. [Project Objectives](#-project-objectives)
4. [Key Features](#-key-features)
5. [Technology Stack](#-technology-stack)
6. [How the System Works](#-how-the-system-works)
7. [Smart Matching Algorithm](#-smart-matching-algorithm)
8. [Project Structure](#-project-structure)
9. [System Requirements](#-system-requirements)
10. [Installation and Setup](#-installation-and-setup)
11. [Database Information](#-database-information)
12. [Application Usage](#-application-usage)
13. [Troubleshooting](#-troubleshooting)
14. [Future Enhancements](#-future-enhancements)
15. [Project Team](#-project-team)
16. [Academic Information](#-academic-information)

---

## 📖 About the Project

Smart Lost & Found System is a web-based application developed using Python and Flask.

The main purpose of this project is to provide a centralized platform where users can report lost items and register found items.

The system helps users identify potentially matching lost and found belongings through a score-based matching algorithm.

It also provides features such as user authentication, item searching, claim management, notifications, messaging, and user dashboards.

The application aims to make the process of recovering lost belongings easier, faster, and more organized.

---

## ❗ Problem Statement

In colleges, universities, offices, and public places, people frequently lose their personal belongings.

Traditional lost and found processes usually depend on manual communication, notice boards, or security offices.

These methods create several problems:

- Difficulty in finding lost belongings.
- No centralized platform for lost and found reports.
- Time-consuming manual searching.
- Difficulty in connecting owners with finders.
- Lack of proper claim tracking and communication.

### Our Solution

Smart Lost & Found System provides a digital platform that connects people who have lost their belongings with people who have found them.

Users can report items, search existing reports, receive possible matches, and communicate through the platform.

---

## 🎯 Project Objectives

- To develop a centralized lost and found platform.
- To simplify the process of reporting lost and found items.
- To identify potential matches automatically.
- To connect item owners with finders.
- To provide a secure claim management process.
- To reduce the time and effort required to recover lost belongings.
- To create a responsive and user-friendly web application.

---

## ✨ Key Features

### 1. User Authentication
- User registration and login.
- Password hashing for security.
- Session-based authentication.
- Protected user pages.

### 2. Lost Item Reporting
- Users can report their lost belongings.
- Add item name, category, location, and description.
- Upload item images.
- View submitted reports.

### 3. Found Item Reporting
- Users can report items they have found.
- Add item details and location.
- Upload item photographs.
- Help rightful owners identify their belongings.

### 4. Smart Matching System
- Automatically compares lost and found reports.
- Calculates a matching score.
- Identifies potential matches based on item details.
- Displays possible matching reports.

### 5. Search and Filtering
- Search items by name.
- Filter by category.
- Filter by report type.
- Search using location information.

### 6. Claim Management
- Users can submit claims for their belongings.
- Item owners can review claim requests.
- Claims can be approved or rejected.
- Users can track their claim status.

### 7. Notification System
- Notifications for important activities.
- Updates related to claims and reports.
- Unread notification tracking.

### 8. Messaging System
- Users can communicate with each other.
- Socket.IO support for real-time communication.
- Messaging interface for discussing item recovery.

### 9. User Dashboard
- View personal reports.
- Track lost and found items.
- View claim information.
- Check recent activities and notifications.

### 10. Responsive User Interface
- Clean and modern interface.
- Mobile-friendly layout.
- Desktop and mobile support.

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Template Engine | Jinja2 |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Real-Time Communication | Flask-SocketIO, Socket.IO |
| Authentication | Flask Sessions |
| Password Security | Werkzeug |
| Version Control | Git and GitHub |
| Deployment | Render |

### Technologies Explained

**Python:** Main programming language used for backend development.

**Flask:** Lightweight Python web framework used to develop application routes and backend functionality.

**HTML, CSS and JavaScript:** Used to create the user interface and frontend interactions.

**Jinja2:** Used to dynamically display data inside HTML templates.

**SQLite:** Lightweight database used to store user accounts, reports, claims, messages, and notifications.

**Flask-SQLAlchemy:** Used to interact with the SQLite database through Python models.

**Flask-SocketIO:** Provides real-time communication functionality.

**Werkzeug:** Used for password hashing and related security utilities.

---

## ⚙️ How the System Works

The basic workflow of the application is:

1. A user creates an account or logs in.
2. The user reports a lost item or a found item.
3. The application stores the report in the database.
4. The matching system compares relevant lost and found reports.
5. Potential matches are displayed to users.
6. The user can submit a claim for a matching item.
7. The item owner reviews the claim.
8. After approval, users can communicate through the messaging system.
9. The item can be returned to its rightful owner.

### Basic Workflow

```text
       User Registration / Login
                  |
                  v
          User Dashboard
                  |
          +-------+-------+
          |               |
          v               v
     Report Lost     Report Found
          |               |
          +-------+-------+
                  |
                  v
          Database Storage
                  |
                  v
         Smart Matching System
                  |
                  v
          Potential Matches
                  |
                  v
            Submit Claim
                  |
                  v
          Claim Verification
                  |
           +------+------+
           |             |
           v             v
        Approved       Rejected
           |
           v
       Communication
           |
           v
       Item Recovery
```

---

## 🧠 Smart Matching Algorithm

The application uses a score-based matching algorithm to identify possible matches between lost and found items.

The matching score is calculated using four criteria:

| Matching Criteria | Weight |
|---|---:|
| Category Match | 40 |
| Location Match | 30 |
| Item Name Match | 20 |
| Common Description Words | 10 |
| **Maximum Score** | **100** |

### Matching Process

1. The system compares the category of lost and found items.
2. It checks whether the reported locations match.
3. It compares item names.
4. It checks common words in item descriptions.
5. It calculates the total matching score.

### Matching Formula

```text
Total Match Score =
Category Score +
Location Score +
Name Score +
Description Score
```

Items having a matching score of 40 or above are considered potential matches.

**Note:** A matching score indicates similarity between reports. It does not guarantee that two reports refer to the same physical item. Ownership should be verified before returning an item.

---

## 📂 Project Structure

```text
Smart-Lost-and-Found/
│
├── instance/
│   └── lost_found.db
│
├── static/
│   ├── images/
│   │   ├── backpack.jpg
│   │   ├── found.jpg
│   │   ├── report.jpg
│   │   ├── search.jpg
│   │   ├── smartphone.jpg
│   │   └── wallet.jpg
│   │
│   ├── js/
│   │   └── socket.io.min.js
│   │
│   ├── uploads/
│   │   └── Uploaded item images
│   │
│   ├── script.js
│   ├── socket.io.min.js
│   └── style.css
│
├── templates/
│   ├── base.html
│   ├── claim.html
│   ├── claim_detail.html
│   ├── claims.html
│   ├── contact_found.html
│   ├── dashboard.html
│   ├── found.html
│   ├── index.html
│   ├── item.html
│   ├── items.html
│   ├── login.html
│   ├── lost.html
│   ├── matches.html
│   ├── messages.html
│   ├── my_reports.html
│   ├── notifications.html
│   ├── profile.html
│   ├── register.html
│   └── search.html
│
├── .gitignore
├── app.py
├── models.py
├── package.json
├── package-lock.json
└── requirements.txt
```

### Important Files and Folders

| File/Folder | Description |
|---|---|
| `app.py` | Main Flask application and application routes |
| `models.py` | Database models |
| `requirements.txt` | Python dependencies |
| `package.json` | Node.js package configuration |
| `templates/` | HTML templates |
| `static/` | CSS, JavaScript, images, and static files |
| `static/uploads/` | Uploaded item images |
| `instance/` | Application instance data |
| `lost_found.db` | SQLite database file |
| `.gitignore` | Specifies files Git should ignore |

---

## 💻 System Requirements

Before running the project, make sure your computer has:

| Requirement | Recommended |
|---|---|
| Operating System | Windows 10/11, Linux or macOS |
| Python | Python 3.x |
| Code Editor | VS Code |
| Web Browser | Chrome, Edge or Firefox |
| RAM | 4 GB or above |
| Internet | Required for cloning and installing dependencies |

You can check whether Python is installed:

```bash
python --version
```

You should also have Git installed:

```bash
git --version
```

---

## 🚀 Installation and Setup

Follow these steps to run the application on your local computer.

### Step 1: Clone the Repository

Open Command Prompt or VS Code Terminal.

Run:

```bash
git clone https://github.com/thakuravinashji/smart-lost-found.git
```

Move into the project directory:

```bash
cd smart-lost-found
```

**What does this do?**

It downloads the project source code from GitHub to your computer.

### Step 2: Create a Virtual Environment

Run:

```bash
python -m venv venv
```

**Why is this required?**

A virtual environment keeps the Python dependencies of this project separate from other Python projects on your computer.

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate
```

For Linux/macOS:

```bash
source venv/bin/activate
```

After activation, you should see `(venv)` at the beginning of your terminal line.

**If PowerShell blocks activation**, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### Step 4: Install Python Dependencies

Run:

```bash
pip install -r requirements.txt
```

**What does this do?**

It installs all the Python libraries required by the application, including Flask and other project dependencies.

### Step 5: Run the Application

Run:

```bash
python app.py
```

The Flask application will start if the installation and configuration are successful.

### Step 6: Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

You can now use the Smart Lost & Found System locally.

---

## 🗄️ Database Information

This project uses SQLite as its database.

The database file is:

```text
instance/lost_found.db
```

The application uses Flask-SQLAlchemy to interact with the database.

### Database Models

The application contains the following main models:

| Model | Purpose |
|---|---|
| User | Stores user information |
| Item | Stores lost and found item details |
| Claim | Manages ownership claims |
| Notification | Stores user notifications |
| Message | Stores user messages |

### Database Notes

- SQLite does not require a separate database server.
- The database is stored as a local file.
- Do not delete the database while the application is running.
- Keep backups of important database information.
- If the database file is not included in a fresh clone, make sure the application's database initialization process creates it before using the application.

---

## 📱 Application Usage

After starting the application, follow these steps:

### 1. Register

- Open the application.
- Navigate to the registration page.
- Enter the required details.
- Create your account.

### 2. Login

- Enter your registered credentials.
- Access your dashboard.

### 3. Report a Lost Item

- Open the Lost Item section.
- Enter item details.
- Add the location and description.
- Upload an image if available.
- Submit the report.

### 4. Report a Found Item

- Open the Found Item section.
- Enter the found item's details.
- Add its location and description.
- Upload an image if available.
- Submit the report.

### 5. Search for Items

- Open the Search page.
- Enter an item name or keyword.
- Apply available filters.
- View matching reports.

### 6. Check Possible Matches

- Open the Matches section.
- Review the suggested matching items.
- Compare item details.

### 7. Submit a Claim

- Select the relevant found item.
- Submit a claim to establish ownership.
- Wait for the item owner's decision.

### 8. Manage Notifications and Messages

- Open Notifications to view updates.
- Use the messaging feature to communicate with other users.

---

## 🔐 Security Features

The application includes several security-related features:

- Password hashing using Werkzeug.
- Session-based user authentication.
- Login protection for restricted pages.
- User-specific data handling.
- Claim approval and rejection workflow.

**Security Recommendation:** For production deployment, use a strong secret key, secure session settings, HTTPS, and appropriate database backups. Never commit passwords, secret keys, or private credentials to GitHub.

---

## ⚠️ Troubleshooting

If you face any problems while running the application, try these solutions.

### Problem 1: Python is not recognized

**Error:**

```text
'python' is not recognized as an internal or external command
```

**Solution:**

- Install Python.
- Enable the Add Python to PATH option during installation.
- Restart the terminal.
- Check Python using:

```bash
python --version
```

### Problem 2: Module Not Found

**Error:**

```text
ModuleNotFoundError: No module named 'flask'
```

**Solution:**

Activate your virtual environment and run:

```bash
pip install -r requirements.txt
```

### Problem 3: Port Already in Use

**Error:**

```text
Address already in use
```

**Solution:**

Another application may already be using port 5000.

Stop the other application or configure a different available port.

### Problem 4: Virtual Environment Not Activating

For PowerShell, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

### Problem 5: Database Error

Check the database configuration and ensure the `instance` directory exists.

If you are using an existing database, avoid deleting or replacing it without taking a backup.

---

## 🔮 Future Enhancements

The following features can be considered for future development:

- AI-based image recognition.
- Mobile application support.
- GPS-based location matching.
- Email and SMS notifications.
- Advanced search and filtering.
- Improved user verification.
- Enhanced analytics and reporting.

---

## 👨‍💻 Project Team

This project was developed by:

| S. No. | Team Member | Role |
|---|---|---|
| 1 | Avinash Kumar Thakur | Team Leader |
| 2 | Aryan Srivastava | Team Member |
| 3 | Ashish Jaiswal | Team Member |
| 4 | Ashvani Kushwaha | Team Member |
| 5 | Aditya Singh | Team Member |

---

## 🎓 Academic Information

| Details | Information |
|---|---|
| Project Title | Smart Lost & Found System |
| Project Type | College Mini Project |
| Department | Computer Science & Engineering |
| College | Maharana Pratap Engineering College |
| Location | Kanpur, Uttar Pradesh |

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

If you want to contribute:

1. Fork this repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Submit a Pull Request.

---

## 📜 License

This project is developed as an academic mini project.

Please contact the project team before redistributing or using the project commercially.

---

## ❤️ Acknowledgement

We sincerely thank our project guide, faculty members, and college for their valuable guidance and support throughout the development of this project.

---

<p align="center">
  <b>Smart Lost & Found System</b><br>
  Making Lost Item Recovery Easier and Smarter.
  <br><br>
  Developed with ❤️ by Team Smart Lost & Found
</p>
