import re
import json
import sys
from bs4 import BeautifulSoup
from pinger import multi_ping_query
from urllib2 import urlopen, Request
from exc import ProfileNotFound
from iso_country_codes import COUNTRY


def get_fav_server(username, category=0, limit=None, verbose=False, ping=True, ping_step=5):
    """
    Scrapes user's profile to find the favorite servers and return their IP addresses

    :param username: Battlelog username
    :param category: 0 for favorite server or 1 for recently played server
    :param ping: Boolean. Whether server ping is desired or not
    :param verbose: Boolean. To get verbose output as the script progresses
    :param ping_step: Number of servers to ping at once. Using a large value may result in incorrect (higher) ping.
                      Default has been set to 5 which should be good even for even a weak/slow internet connection.

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
        print "Gathering server information..."
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
        server.queued_players = int(json_data[u'message'][u'SERVER_INFO'][u'numQueued'])
        server.country_code = json_data[u'message'][u'SERVER_INFO'][u'country']
        server.country = COUNTRY[server.country_code.upper()]
        server.region = json_data[u'message'][u'SERVER_INFO'][u'region']
        server.ranked = json_data[u'message'][u'SERVER_INFO'][u'ranked']
        server.punkbuster = json_data[u'message'][u'SERVER_INFO'][u'punkbuster']
        server.port = json_data[u'message'][u'SERVER_INFO'][u'port']
        server.has_password = json_data[u'message'][u'SERVER_INFO'][u'hasPassword']
        server.game_mode = int(json_data[u'message'][u'SERVER_INFO'][u'mapMode'])
        server.map_code = json_data[u'message'][u'SERVER_INFO'][u'map']
        server.map_list = json_data[u'message'][u'SERVER_INFO'][u'maps']
        server_list.append(server)
    if ping:
        if verbose:
            print "Now pinging the servers..."
        server_list = send_ping(server_list, ping_step)
    if verbose:
        for server in server_list:
            print server
        print '\nFinished...\n'
    # Removing duplicate servers
    server_list = list(set(server_list))
    # Returning the list of BF3Server objects
    return server_list


def browse_server(limit=30, ping=True):
    main_json_data = []
    # calculating how many times we have to loop
    repeat = limit / 30
    base_url = "http://battlelog.battlefield.com/bf3/servers/getAutoBrowseServers/" \
               "?filtered=1&slots=1&slots=2&slots=4&slots=16&offset=%d"
    for i in range(repeat + 1):
        offset = 30 * repeat
        req = Request(base_url % offset)
        req.add_header("X-Requested-With", "XMLHttpRequest")
        json_data = json.loads(urlopen(req).read())
        main_json_data += json_data['data']
    server_list = []
    for server_data in main_json_data[:limit]:
        server = BF3Server()
        server.name = server_data['name']
        server.guid = server_data['guid']
        server.ip = server_data['ip']
        server.url = "http://battlelog.battlefield.com/bf3/servers/show/%s/" % server.guid
        server.max_players = server_data['maxPlayers']
        server.num_players = server_data['numPlayers']
        server.queued_players = int(server_data['numQueued'])
        server.country_code = server_data['country']
        server.country = COUNTRY[server.country_code.upper()]
        server.region = server_data['region']
        server.ranked = server_data['ranked']
        server.punkbuster = server_data['punkbuster']
        server.port = server_data['port']
        server.has_password = server_data['hasPassword']
        server.game_mode = int(server_data['mapMode'])
        server.map_code = server_data['map']
        server_list.append(server)
    # Removing duplicate servers
    server_list = list(set(server_list))
    if ping:
        server_list = send_ping(server_list)
    return server_list


def send_ping(servers, repeat=3, ping_step=5):
    ip_list = [x.ip for x in servers]
    ping_list = []
    # Repeating the ping process.
    for _ in range(repeat):
        # Passing ip_list[:] because ping_list() is performing pop on the passed list with same reference.
        ping_list.append(multi_ping_query(ip_list[:], timeout=1, step=ping_step, host_lookup=False))
    for server in servers:
        # Collecting ping values for current server in a list.
        pings = [x[server.ip] * 1000 for x in ping_list if x[server.ip]]
        # Removing empty elements with filter and then converting them to integer value.
        pings = map(int, pings)
        # Finding average ping value if the list is not empty else returning 9999.
        if len(pings):
            server.ping = sum(pings) / len(pings)
        else:
            server.ping = 9999
    # Sorting the server list based on ping
    servers.sort(key=lambda x: x.ping)
    return servers


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
        self.queued_players = 0
        self.country = ''
        self.region = ''
        self.ranked = False
        self.punkbuster = False
        self.port = 0
        self.has_password = False
        self.game_mode = ''
        self.map_code = ''
        self.map_list = []

    def __str__(self):
        response = "\nServer Name: " + self.name
        response += "\nServer IP: " + self.ip
        response += "  |  Ping: " + str(self.ping) + "ms"
        return response

    def __eq__(self, other):
        return self.guid == other.guid

    def __hash__(self):
        return hash(self.guid)

    # Dictionary containing Map Names and their respective id
    map_code = {
        "MP_001": "Grand Bazaar",
        "MP_003": "Tehran Highway",
        "MP_007": "Caspian Border",
        "MP_011": "Seine Crossing",
        "MP_012": "Operation Firestorm",
        "MP_013": "Damavand Peak",
        "MP_017": "Noshahr Canals",
        "MP_018": "Kharg Island",
        "MP_Subway": "Operation Metro",
        "XP1_001": "Strike at Karkand",
        "XP1_002": "Gulf of Oman",
        "XP1_003": "Sharqi Peninsula",
        "XP1_004": "Wake Island",
        "XP2_Factory": "Scrapmetal",
        "XP2_Office": "Operation 925",
        "XP2_Palace": "Donya Fortress",
        "XP2_Skybar": "Ziba Tower",
        "XP3_Alborz": "Alborz Mountains",
        "XP3_Desert": "Bandar Desert",
        "XP3_Shield": "Armored Shield",
        "XP3_Valley": "Death Valley",
        "XP4_FD": "Markaz Monolith",
        "XP4_Parl": "Azadi Palace",
        "XP4_Quake": "Epicenter",
        "XP4_Rubble": "Talah Market",
        "XP5_001": "Operation Riverside",
        "XP5_002": "Nebandan Flats",
        "XP5_003": "Kiasar Railroad",
        "XP5_004": "Sabalan Pipeline"
    }

    # Dictionary containing game mode names and their respective id
    game_mode = {
        1: "Conquest",
        2: "Rush",
        4: "Squad Rush",
        8: "Squad DM",
        32: "Team DM",
        64: "Conquest Large",
        128: "Conquest Assault Large",
        256: "Conquest Assault",
        512: "Gun Master",
        1024: "Conquest Domination",
        2048: "Team DM 16 Players",
        131072: "Tank Superiority",
        524288: "Capture the Flag",
        4194304: "Scavenger",
        8388608: "Air Superiority"
    }

    # Dictionary containing game sizes and their respective id
    game_size = {
        16: "16",
        24: "24",
        32: "32",
        48: "48",
        64: "64",
        0: "Other"
    }

    # Dictionary containing free slot info and their respective id
    free_slots = {
        16: "Full",
        1: "1-5",
        2: "6-10",
        4: "10+",
        8: "Empty"
    }

    # Dictionary containing presets and their respective id
    preset = {
        1: "Normal",
        2: "Hardcore",
        4: "Infantry Only"
    }

    # Dictionary containing base game with DLCs and their respective id
    game = {
        0: "Battlefield 3",
        512: "Back to Karkand",
        2048: "Close Quarters",
        4096: "Armored Kill",
        8192: "Aftermath",
        16384: "End Game"
    }

if __name__ == '__main__':
    if len(sys.argv) == 2:
        get_fav_server(sys.argv[1], verbose=True)
    else:
        get_fav_server('GuruBabaBangali', verbose=True)
#    print send_ping('216.185.114.85')