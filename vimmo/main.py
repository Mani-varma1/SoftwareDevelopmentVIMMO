from vimmo.API import app

def main():
    app.run(host="os.popen("docker network inspect bridge --format='{{(index .IPAM.Config 0).Gateway}}'").read().strip()", port=5001, debug=True)

if __name__ == '__main__':
    main()
