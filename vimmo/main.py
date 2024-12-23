from vimmo.API import app

def main():
    app.run(host="127.0.0.1", port=5001, debug=True)

if __name__ == '__main__':
    main()