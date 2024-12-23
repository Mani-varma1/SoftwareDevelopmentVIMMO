from vimmo.API import app
import os

def main():
    app.run(host=os.environ.get("BACKEND_HOST", "127.0.0.1"), port=5001, debug=True)

if __name__ == '__main__':
    main()
