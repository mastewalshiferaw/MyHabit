# MyHabit API

This is the backend API project for MyHabit, a personal habit tracker designed for effective habit management. The core problem this project solves is the lack of motivation that comes from generic tracking. It will provide smart, type-specific feedback like "clean streaks" for habits I am quitting and "success streaks" for habits I am building.

## Project Status
This project is complete and meets all the core requirements. The API is fully functional for user authentication, habit management, progress logging, and statistics calculation.

## Technologies Used
*   Python
*   Django & Django Rest Framework
*   Simple JWT (for token authentication)
*   SQLite3 (for the development database)

## Getting Started / Local Setup

To run this project on your local machine, please follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/mastewalshiferaw/MyHabit.git
    cd MyHabit
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the database migrations:**
    ```sh
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel:**
    ```sh
    python manage.py createsuperuser
    ```

6.  **Start the development server:**
    ```sh
    python manage.py runserver
    ```
    The API will now be running at `http://127.0.0.1:8000/`.

## API Usage Guide

Here is a step-by-step guide on how to interact with the MyHabit API.

### 1. Registration

First, create a new user account.

*   **Endpoint:** `POST /api/auth/register/`
*   **Request Body:**
    ```json
    {
        "username": "mark",
        "password": "Password123",
        "email": "mark@email.com"
    }
    ```
*   **Success Response:** `201 Created`

### 2. Log In to Get an Access Token

Next, log in with your new credentials to get a JWT access token. This token must be included in the header of all future requests.

*   **Endpoint:** `POST /api/auth/token/`
*   **Request Body:**
    ```json
    {
        "username": "mark",
        "password": "Password123"
    }
    ```
*   **Success Response:** `200 OK`, returning `access` and `refresh` tokens.

### 3. Create a New Habit

As an authenticated user, you can create a new habit.

*   **Endpoint:** `POST /api/habits/`
*   **Authorization:** `Bearer <your_access_token>`
*   **Request Body:**
    ```json
    {
        "name": "Read every day",
        "habit_type": "BUILD"
    }
    ```
*   **Success Response:** `201 Created`, returning the new habit object.

### 4. Log a Habit Completion

Log your progress for a specific habit using its ID.

*   **Endpoint:** `POST /api/habits/{id}/log/`
*   **Authorization:** `Bearer <your_access_token>`
*   **Request Body:**
    ```json
    {
        "completion_date": "2024-08-25"
    }
    ```
*   **Success Response:** `201 Created`.

### 5. Get Habit Statistics

Retrieve the calculated streaks for a specific habit.

*   **Endpoint:** `GET /api/habits/{id}/stats/`
*   **Authorization:** `Bearer <your_access_token>`
*   **Success Response:** `200 OK`, returning an object with `current_streak` and `longest_streak`.