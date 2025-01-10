# Webhook Repo: GitHub Event Tracker

This repository contains a Flask application that serves as a webhook endpoint to track GitHub events (Push, Pull Request, Merge) from a connected repository (`action-repo`). It stores the events in a MongoDB database and provides a simple UI to display them.

## Project Overview

This project is a solution to the following problem statement:

> **Build a GitHub repository which automatically sends an event (webhook) on the following GitHub actions ("Push", "Pull Request", "Merge") to a registered endpoint, and store it to MongoDB.**
>
> **The UI will keep pulling data from MongoDB every 15 seconds and display the latest changes to the repo in the below format:**
>
> **For PUSH action:**
>
> *   Format: `{author} pushed to {to_branch} on {timestamp}`
> *   Sample: `"Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC`
>
> **For PULL_REQUEST action:**
>
> *   Format: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`
> *   Sample: `"Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC`
>
> **For MERGE action:**
>
> *   Format: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`
> *   Sample: `"Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC`

This repository (`webhook-repo`) implements the webhook endpoint and UI, while a separate repository (`action-repo`) is used to trigger the GitHub events.

## Planned Improvements:
I'm planning to add websockets in order to stop polling and maintain a persistent connection. This will let me see live changes as they happen in the repo. 

## Features

*   **Webhook Endpoint:** A Flask-based webhook endpoint (`/webhook`) that receives GitHub webhook events.
*   **Event Processing:** Processes `Push`, `Pull Request`, and `Merge` events (with special handling for merge events using the `pull_request` `closed` action and `merged` status).
*   **MongoDB Storage:** Stores event data in a MongoDB database with the following schema:
    | Field        | Datatype       | Details                                                                                             |
    | :----------- | :------------- | :-------------------------------------------------------------------------------------------------- |
    | `_id`        | `ObjectID`     | MongoDB default ID                                                                                  |
    | `request_id` | `string`       | Git commit hash (for pushes) or Pull Request ID, or a hash for merge events                          |
    | `author`     | `string`       | Name of the GitHub user making the action                                                           |
    | `action`     | `string`       | Type of action ("PUSH", "PULL_REQUEST", "MERGE")                                                   |
    | `from_branch`| `string`       | Name of the source branch (for pull requests and merges)                                          |
    | `to_branch`  | `string`       | Name of the target branch (for pushes, pull requests, and merges)                                 |
    | `timestamp`  | `string(datetime)` | Timestamp of the action (UTC)                                                                    |
*   **UI:** A simple HTML/CSS/JavaScript frontend that polls the backend (using the `/events` endpoint) every 15 seconds to display the latest events in a user-friendly format.
*   **Error Handling:** Includes error handling for invalid webhook payloads and unexpected errors.

## Prerequisites

*   **Python 3:** Make sure you have Python 3 installed on your system.
*   **pip:** Python's package installer.
*   **MongoDB:** A running MongoDB instance (locally or remotely, the code uses a remote instance).
*   **Ngrok (or a similar tunneling service):** To expose your local Flask app to the internet for testing webhooks.

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd webhook-repo
    ```

2. **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment:**

    *   **macOS/Linux:** `source venv/bin/activate`
    *   **Windows:** `venv\Scripts\activate`

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    (Make sure you create a `requirements.txt` file with the necessary packages: `flask`, `pymongo`, `python-dotenv`)

5. **Configure environment variables:**
    *   Create a `.env` file in the root directory.
    *   Add the following environment variables:

        ```
        MONGO_URI=your_mongodb_connection_string
        # Optional for enhanced security:
        GITHUB_WEBHOOK_SECRET=your_webhook_secret
        ```

        Replace `your_mongodb_connection_string` with your actual MongoDB connection string and `your_webhook_secret` with a strong secret token if you're implementing webhook signature verification.

6. **Set up Ngrok (or a similar tunnel):**
    *   Install Ngrok from [https://ngrok.com/](https://ngrok.com/).
    *   If you have a paid Ngrok account and want to use a static domain, configure it in your `ngrok.yml` file (see Ngrok documentation for details).

7. **Configure GitHub Webhook in `action-repo`:**
    *   Go to your `action-repo` on GitHub.
    *   Go to "Settings" -> "Webhooks" -> "Add webhook."
    *   **Payload URL:**
        *   If using Ngrok without a static domain: `http://<your-ngrok-subdomain>.ngrok.io/webhook`
        *   If using Ngrok with a static domain: `https://<your-static-domain>.ngrok-free.app/webhook`
    *   **Content type:** `application/json`
    *   **Secret:** (Optional) Enter the same secret token you set in your `.env` file as `GITHUB_WEBHOOK_SECRET`.
    *   **Events:** Select "Let me select individual events" and choose "Pushes" and "Pull requests."
    *   **Active:** Check the "Active" box.
    *   Click "Add webhook."

## Running the Application

1. **Start MongoDB:** Make sure your MongoDB server is running.
2. **Start the Flask app:**

    ```bash
    flask run --port=5000
    ```

3. **Start Ngrok (if needed):**

    *   **Without static domain:**

        ```bash
        ngrok http 5000
        ```

    *   **With static domain:** (Make sure you've configured `ngrok.yml` correctly)

        ```bash
        ngrok start <your_tunnel_name>
        ```

        (Replace `<your_tunnel_name>` with the name of the tunnel you defined in `ngrok.yml`)

4. **Access the UI:** Open your browser and go to:
    *   If using Ngrok: `http://<your-ngrok-subdomain>.ngrok.io` or `https://<your-static-domain>.ngrok-free.app`
    *   If not using Ngrok (for local testing only): `http://localhost:5000`

## Testing

1. **Trigger Events:** Perform actions in your `action-repo` (push code, create pull requests, merge pull requests).


## Code Structure

*   **`app.py`:** The main Flask application file.
    *   Defines the webhook endpoint (`/webhook`).
    *   Handles event processing (`process_push`, `process_pull_request`, `process_merge`).
    *   Provides the `/events` endpoint for the UI to fetch data.
    *   Serves the static `index.html` file.
*   **`templates/index.html`:** The HTML, CSS, and JavaScript for the frontend UI.
*   **`requirements.txt`:** Lists the required Python packages.
*   **`.env`:** Stores environment variables (MongoDB connection string, webhook secret).

## Further Improvements

*   **Enhanced UI:** Consider using a frontend framework like React to create a more dynamic and interactive UI.
*   **Real-time Updates:** Implement WebSockets (e.g., using SocketIO) to push updates to the UI in real-time instead of relying solely on polling.
*   **Authentication:** Add authentication to protect the `/events` endpoint.
*   **More Robust Error Handling:** Implement more comprehensive error handling and logging.
*   **Deployment:** Deploy the application to a production server (e.g., Heroku, AWS, DigitalOcean) for a more permanent setup.
*   **Automated Tests:** Write unit and integration tests to ensure code quality and prevent regressions.

## Related Repository

*   **`action-repo`:** https://github.com/khilav23/action-repo - This is the repository that triggers the GitHub webhook events.

