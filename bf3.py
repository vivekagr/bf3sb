import re
import json
import sys
from bs4 import BeautifulSoup
from pinger import do_one
from urllib2 import urlopen
from exc import ProfileNotFound


def get_fav_server(username, category=0, ping=True, verbose=False, limit=None):
    """
    Scrapes user's profile to find the favorite servers and return their IP addresses

    :param username: Battlelog username
    :param category: 0 for favorite server or 1 for recently played server
    :param ping: Boolean. Whether server ping is desired or not
    :param verbose: Boolean. To get verbose output as the script progresses

    Profile's server section contains two div with class 'box'.

    First div contains the favorite server information and the second contains recently played
    server information.
    """
    profile_url = "http://battlelog.battlefield.com/bf3/user/%s/servers/" % username
    raw_html = urlopen(profile_url).read()
    if "that page doesn't exist" in raw_html:
        if verbose:
            print "Profile with username '%s' doesn't exists." % username
            sys.exit()
        raise ProfileNotFound(username)
    data = BeautifulSoup(raw_html)
    server_div = data.find_all(class_='box')[category]
    # Parsing out the server url which contains server guid
    server_urls = [x.find('a').get('href') for x in server_div.find_all(class_='profile-serverbookmark-info-name')]
    # Now we parse out the 36 char server guid
    guids = [re.findall('show/([a-z0-9-]{36})/', url)[0] for url in server_urls]
    if limit:
        guids = guids[:int(limit)]
    if verbose:
        type_ = 'favorite' if category == 0 else 'recently played'
        print "Found {} {} servers from {}'s profile...".format(len(guids), type_, username)
        if ping:
            print "Please wait while the servers are being pinged..."
    server_list = []
    # Fetching Server IP address (along with some other info), making new BF3Server object and adding the info to it
    for guid in guids:
        url = "http://battlelog.battlefield.com/bf3/servers/show/%s/?json=1" % guid
        json_data = json.loads(urlopen(url).read())
        server = BF3Server()
        server.name = json_data[u'message'][u'SERVER_INFO'][u'name']
        server.guid = guid
        server.ip = json_data[u'message'][u'SERVER_INFO'][u'ip']
        server.url = "http://battlelog.battlefield.com/bf3/servers/show/%s/" % guid
        server.max_players = json_data[u'message'][u'SERVER_INFO'][u'maxPlayers']
        server.num_players = json_data[u'message'][u'SERVER_INFO'][u'numPlayers']
        server.country = json_data[u'message'][u'SERVER_INFO'][u'country']
        server.ranked = json_data[u'message'][u'SERVER_INFO'][u'ranked']
        server.punkbuster = json_data[u'message'][u'SERVER_INFO'][u'punkbuster']
        server.port = json_data[u'message'][u'SERVER_INFO'][u'port']
        server_list.append(server)
        if ping:
            server.ping = send_ping(server.ip)
        if verbose:
            print server
    if verbose:
        print '\nFinished...\n'
    server_list.sort(key=lambda x: x.ping)
    # Returning the list of BF3Server objects
    return server_list


def send_ping(host, count=3):
    """
    Pings the hostname given number of times and returns the average ping time.
    :param host: hostname
    :param count: number of times to ping
    :return: ping time in milliseconds, 9999 if timed out
    """
    ping_time = [do_one(host) for _ in range(count)]
    # Filtering out None
    ping_time = filter(lambda x: x is not None, ping_time)
    if len(ping_time) == 0:
        return 9999
    avg = sum(ping_time) / len(ping_time)
    ping = int(avg * 1000)
    return ping


class BF3Server:
    """
    Class representing a BF3 Server
    """
    def __init__(self):
        self.name = ''
        self.guid = ''
        self.ip = ''
        self.url = ''
        self.ping = ''
        self.max_players = 0
        self.num_players = 0
        self.country = ''
        self.ranked = False
        self.punkbuster = False
        self.port = 0

    def __str__(self):
        response = "\nServer Name: " + self.name
#        response += "\nServer GUID:" + self.guid
        response += "\nServer IP: " + self.ip
#        response += "\nServer URL:" + self.url
        response += "  |  Ping: " + str(self.ping) + "ms"
        return response


if __name__ == '__main__':
    if len(sys.argv) == 2:
        get_fav_server(sys.argv[1], verbose=True)
    else:
        get_fav_server('GuruBabaBangali', verbose=True)
#    print send_ping('216.185.114.85')