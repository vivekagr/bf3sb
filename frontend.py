from flask import Flask, url_for, render_template, request, flash, redirect
from urllib2 import URLError
from bf3 import get_fav_server
from exc import ProfileNotFound

app = Flask(__name__)
app.secret_key = "jdawdwaddd;dl2;dld'.,929d2jddw/"

@app.route('/')
def index():
    return render_template('fav_form.html')

@app.route('/fav/', methods=['POST'])
def fav():
    """
    Takes in username and category as arguments and shows the result.
    """
    if not request.form['username']:
        flash("No username submitted")
        return redirect(url_for('index'))

    user = request.form['username']
    type_ = request.form['serverType']

    try:
        if request.form['limit']:
            server_list = get_fav_server(user, int(type_), limit=request.form['limit'])
        else:
            server_list = get_fav_server(user, int(type_))

    except ProfileNotFound as e:
        flash("Battlelog profile with username '%s' doesn't exist" % e.args[0])
        return redirect(url_for('index'))

    except URLError as e:
        flash("Network Error: %s" % e.args[0])
        return redirect(url_for('index'))

    else:
        return render_template('favorite.html', user=user, type_=type_, servers=server_list)

if __name__ == '__main__':
    app.run(debug=True)