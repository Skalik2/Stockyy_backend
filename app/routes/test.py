from app import app

@app.route('/')
def test():
    return "Server is running!"
