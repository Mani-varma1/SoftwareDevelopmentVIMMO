from APIapp import app  # Import the Flask application instance named `app` from a module named `APIapp`

# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    # Run the Flask application
    app.run(host="127.0.0.1", port=5000, debug=True)