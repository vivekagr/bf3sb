from flask import Flask, url_for, render_template, request, flash, redirect
from urllib2 import URLError
from bf3 import get_fav_server, BF3Server, browse_server, ProfileNotFoundError
from socket import error as socket_error
from time import time

app = Flask(__name__)
app.secret_key = "jdawdwaddd;dl2;dld'.,929d2jddw/"


@app.route('/')
def index():
    return render_template('index.html')


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
        start_time = time()
        if request.form['limit']:
            server_list = get_fav_server(user, int(type_), limit=request.form['limit'])
        else:
            server_list = get_fav_server(user, int(type_))

    except ProfileNotFoundError as e:
        flash("Battlelog profile with username '%s' doesn't exist" % e.args[0])
        return redirect(url_for('index'))

    except URLError as e:
        flash("Network Error: %s" % e.reason)
        return redirect(url_for('index'))

    except socket_error:
        flash("Cannot ping without root privilege. Please restart the application with root/admin privilege.")
        return redirect(url_for('index'))

    else:
        flag_icon_url = "http://battlelog-cdn.battlefield.com/cdnprefix/a/public/common/flags/%s.gif"
        time_elapsed = round(time() - start_time, 2)
        return render_template('output.html', servers=enumerate(server_list), bf3=BF3Server,
                               flag_icon_url=flag_icon_url, time_elapsed=time_elapsed)


@app.route('/browse/', methods=['GET'])
def browse():
    try:
        start_time = time()
        limit_val = request.args.get('limit')
        limit = int(limit_val) if limit_val else 30
        server_list = browse_server(limit=limit)

    except URLError as e:
        flash("Network Error: %s" % e.reason)
        return redirect(url_for('index'))

    except socket_error:
        flash("Cannot ping without root privilege. Please restart the application with root/admin privilege.")
        return redirect(url_for('index'))

    else:
        flag_icon_url = "http://battlelog-cdn.battlefield.com/cdnprefix/a/public/common/flags/%s.gif"
        time_elapsed = round(time() - start_time, 2)
        return render_template('output.html', servers=enumerate(server_list), bf3=BF3Server,
                               flag_icon_url=flag_icon_url, time_elapsed=time_elapsed)

if __name__ == '__main__':
    app.run(debug=True)