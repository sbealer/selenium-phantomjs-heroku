import app

def post_to_hipchat():
    print "Sending not to hipchat"
    app.send_hipchat_note()

if __name__ == "__main__":
    post_to_hipchat()