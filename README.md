# DriveShare

## **Setup and Run Locally**
1. **Clone the Repository**
   ```sh
   git clone https://github.com/leahmirch/DriveShare-Platform.git
   cd DriveShare-Platform
   ```

2. **Create a Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application in a Terminal**
   ```sh
   python app.py
   ```

5. **Access the Site Locally**
   - Open **http://127.0.0.1:5000/** in a web browser.

## **Database**
- This project uses SQLite for simplicity.
- If needed, delete `database.db` to reset the database.

### Accessing the Database
1. **Using SQLite CLI**:
   - Open a terminal or command prompt and navigate to the project directory:
     ```sh
     cd path/to/DriveShare-Platform
     ```
   - Start SQLite with the database file:
     ```sh
     sqlite3 database.db
     ```
   - List all tables:
     ```sql
     .tables
     ```
   - View table schema:
     ```sql
     .schema users
     .schema cars
     ```
   - Run a basic query:
     ```sql
     SELECT * FROM users;
     ```

3. **(Optional) Use DB Browser for SQLite (GUI Tool)**:
   - Download and install [DB Browser for SQLite](https://sqlitebrowser.org/).
   - Open `database.db` in the application.
   - Browse tables, execute queries, and inspect data visually.

### Running Custom Queries
- **Insert Data**:
  ```sql
  INSERT INTO users (email, password, security_q1, security_q2, security_q3) 
  VALUES ('test@example.com', 'securepass', 'Answer1', 'Answer2', 'Answer3');
  ```
- **Update Data**:
  ```sql
  UPDATE users SET password='newpass' WHERE email='test@example.com';
  ```
- **Delete Data**:
  ```sql
  DELETE FROM users WHERE email='test@example.com';
  ```

### Notes
- Always **back up the database** before making modifications.
- Use `.exit` to close SQLite CLI.
- For large queries, prefer using Python or DB Browser.
