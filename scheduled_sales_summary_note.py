import app

def post_to_hipchat():
    print("Sending note to hipchat")
    app.send_hipchat_note('prd')

if __name__ == "__main__":
    post_to_hipchat()