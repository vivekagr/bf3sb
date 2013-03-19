Battlefield 3 (Unofficial) Server Browser
============================

A desktop application (as an alternative to web based Battlelog) for browsing Battlefield 3 servers.

![Application Screenshot](https://github.com/vivekagr/bf3/raw/master/images/app.png "Battlefield 3 Server Browser")


But why?!
----------

Battlelog's ping function doesn't work or is inaccurate with low bandwidth or higher latency connections.

Also I don't like the 30 servers limit and want to be able to get a lot more results.


How does it work?
------------------

This application pings a limited number (which can be set) of servers at a time to prevent the requests from timing out.

On an unstable connection, you might still get incorrect ping.
To solve this problem, you can set the application to repeat the pinging process a specified number of times and then show you 
the average value.

![Settings Dialog](https://github.com/vivekagr/bf3/raw/master/images/settings.png "Settings Dialog")

After the application is done fetching the server data and pinging them, it renders the result in HTML format and opens it in the system's default browser.


Downloads
----------

Both setup and standalone versions are available and hosted on Sourceforge.

* [Setup](http://sourceforge.net/projects/bf3sb/files/setup/) - [32 bit](http://sourceforge.net/projects/bf3sb/files/setup/bf3sb_setup_32bit.exe/download) & [64 bit](http://sourceforge.net/projects/bf3sb/files/setup/bf3sb_setup_64bit.exe/download)
* [Standalone](http://sourceforge.net/projects/bf3sb/files/standalone/) - [32 bit](http://sourceforge.net/projects/bf3sb/files/standalone/BF3%20Server%20Browser%20%2832-bit%29.exe/download) & [64 bit](http://sourceforge.net/projects/bf3sb/files/standalone/BF3%20Server%20Browser%20%2864-bit%29.exe/download)

FAQ
----

__Why does the application asks for administrator privilege?__

To send ICMP requests for pinging, administrator privilege is required.

__What is the difference between the setup and the standalone versions?__

As the names suggest, setup version will install the application and create a desktop shortcut to the application. It is recommended to use the setup rather than the standalone exe.

Standalone version can be executed directly, however it will take a few seconds to start up. Also, your last used filters won't be saved in the standalone version.

__What are the safe values for *"Number of times to repeat ping process"* and *"Number of servers to ping at a time"* options?__

To give you an idea, Battlelog doesn't repeats the pinging process and it pings 30 servers at a time.
* If Battlelog shows you correct ping values, you can safely use a value of 30 or more for the second option and 1 for first option.
* If Battlelog shows you incorrect ping, try with a value in range 10-20. Also, you can try repeating ping process a couple of times.
* If Battlelog doesn't shows you any ping, it is advised to stay below 10 and repeat pinging 2-3 times.

Contributions
--------------

* If you encounter any sort of bug, please open a new issue on this project page or you can email me the details if you don't have a Github account. Please try to provide as much details as you can about the bug. You can also fork this repo and send a pull request if you can fix the bug yourself.
* Base application has all the necessary filters as on the Battlelog. If you wish to add any other feature, please fork this repo and send a pull request.
* If you have any feature suggestion, either open an issue or send me an email describing the feature. I will try to implement it if it seems to be useful.

---------------------------------

This is an independent project by an enthsiasist and is not affiliated with EA or DICE in any way. Battlefield is a trademark or registered trademark of EA Digital Illusions CE AB in the U.S. and/or other countries.