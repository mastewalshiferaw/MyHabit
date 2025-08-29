This is the backend API project for MyHabit, a personal habit tracker designed for effective habit management. The core problem this project solves is the lack of motivation that comes from generic tracking. It will provide smart, type-specific feedback like "clean streaks" for habits I am quitting and "success streaks" for habits I am building.

## API Usage Guide

Here is a step-by-step guide on how to interact with the MyHabit API.

# 1. Registeration 

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