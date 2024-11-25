# Fine-Tuning Text-to-Image AI Model Microservice

This project sets up a Flask microservice to fine-tune a text-to-image AI model using a set of icon images.

## Setup

1. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install required packages:
    ```sh
    pip install Flask transformers torch
    ```

## Running the Application

1. Start the Flask application:
    ```sh
    flask run
    ```

2. Test the upload endpoint:
    ```sh
    curl -X POST http://127.0.0.1:5000/upload -F 'file=@path_to_your_image.jpg' -F 'text=Your description here'
    ```

3. Test the fine-tuning endpoint:
    ```sh
    curl -X POST http://127.0.0.1:5000/fine_tune
    ```

## Files

- `app.py`: The main Flask application file.
- `fine_tune.py`: Contains the function to fine-tune the model.
- `uploads/`: Directory to store uploaded images.
