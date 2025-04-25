from app import create_app
from dotenv import load_dotenv
load_dotenv()

# Initialize the Flask app using the create_app function
app = create_app()

if __name__ == "__main__":
    # Run the Flask app with debugging enabled
    app.run(debug=True)
