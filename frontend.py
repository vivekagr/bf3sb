from flask import Flask, url_for, render_template
from bf3 import BF3Server, get_fav_server

app = Flask(__name__)


@app.route('/fav/', methods=['GET', 'POST'])
def fav():
    """
    Takes in username and category as arguments and shows the result.
    """
    pass

if __name__ == '__main__':
    app.run()