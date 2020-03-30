# TWCManager
TWCManager lets you control the amount of power delivered by a Tesla Wall Connector (TWC) to the car it's charging.  This can save around 6kWh per month when used to track a local green energy source like solar panels on your roof.  It can also avoid drawing grid energy for those without net metering or limit charging to times of day when prices are cheapest.

Due to hardware limitations, TWCManager will not work with Tesla's older High Power Wall Connectors (HPWCs) that were discontinued around April 2016.
UPDATE: and unfortunately also do not work with the V3 wifi TWC's that were released jan 2020.

See **TWCManager Installation.pdf** for how to install and use.

#####################################################################
# This fork works with utility mains current measuring:
#####################################################################

download the forked code to your raspberry pi using this git command:
    $ git clone -b master --single-branch https://github.com/BitterAndReal/TWCManager.git~/TWC

If we measure how many amps are drawn at the utility mains we can protect the main fuse of your house.
And we can use the mains reading to calculate how much green energy we have left to charge the car.


I used the following Raspberry pi zero shield to measure the utility mains current:
3 current and 1 voltage adapter
http://lechacal.com/wiki/index.php?title=RPIZ_CT3V1
http://lechacalshop.com/gb/internetofthing/63-rpizct3v1.html

The current measure shield could be on the same Raspberry Pi as TWCmanager.
If TWC and mains connection are far away from each other it is possible to use two
raspberry pi connected to the same network and using a socket connection.




**this is how you prepare the pi to run the socket-server script:**

    $ sudo apt-get update
    $ sudo apt-get install -y git
    $ sudo apt-get install python3-pip
    $ sudo python3 -m pip install pyserial
    $ sudo apt-get install -y screen

create this file on the Pi:
    $ ​sudo nano ~/socket-server.py
copy the code of this file into it and save it

to start the socket server at boot:
    $ ​sudo nano /etc/rc.local​
Near the end of the file, before the ​exit 0​ line, add:
    su - pi -c "screen -dm -S socketserver sudo python3 /home/pi/socket-server.py"

# How to make serial work on the Raspberry Pi3 , Pi3B+, PiZeroW:
    $ sudo raspi-config
    Select Interfacing Options / Serial
    then specify if you want a Serial console (no)
    then if you want the Serial Port hardware enabled (yes).
    Then use /dev/serial0 in any code which accesses the Serial Port.

    $ sudo apt-get install python-serial
    $ sudo reboot

after you have a ssh connection to your current measure pi you can open the screen with:
    $ screen -r socketserver





If you want to use the dutch smart meter to read the AC utility mains current you could try DSMR-reader for RaspberryPi
This is not tested and not part of this fork but could be a good alternative for the current measure shield.
    
    # DSMR-reader has the following RESTful API.
    # documented here: https://dsmr-reader.readthedocs.io/en/latest/api.html#example-2-fetch-latest-reading
    # Requirements:
    #   Smart meter DSMR version: v2, v4 of v5
    #   Hardware: RaspberryPi 3
    #   OS: Raspbian OS
    #   Python: 3.6+
    #   Database: PostgreSQL 9+
    #   SD disk space: 4+ GB
    #   P1 telegram cable (RJ11 to USB)

    # Request power with DSRM-reader API:
    import requests
    import json

    response = requests.get(
        'http://YOUR-DSMR-URL/api/v2/datalogger/dsmrreading?ordering=-timestamp&limit=1',
        headers={'X-AUTHKEY': 'YOUR-API-KEY'},
    )

    if response and response.status_code == 200:
        json_data = response.json()
        if json_data and 'results' in json_data:
            if 'phase_currently_delivered_l1' in json_data['results']:
               MainsAmpsPhases[0] = results.get('phase_currently_delivered_l1')*1000/230
               MainsAmpsPhases[1] = results.get('phase_currently_delivered_l2')*1000/230
               MainsAmpsPhases[2] = results.get('phase_currently_delivered_l3')*1000/230
    #          phase_currently_delivered_l... (float) - Current electricity used by phase L... (in kW)

          else:
            if debugLevel >= 1:
                print('DSRM-reader Error: {}'.format(response.text))
