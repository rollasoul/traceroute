from datetime import datetime
import time
import subprocess
from subprocess import Popen, PIPE
import socket
import os
import json
import sys

# global data values
data_trace = {}
network_name = sys.argv[1]
print(network_name)

def get_ip(trace_url):
    # get a temporarliy fixed ip-address for URL that can be used
    # throughout scrip to avoid "mutliple ip-address" possibility for
    # certain URLs
    url_ip = socket.gethostbyname(trace_url)
    return url_ip

def traceroute(url_ip, trace_url):
    # clean up text file
    if os.path.exists("trace_client.txt"):
        os.remove("trace_client.txt")
        time.sleep(1)

    # write traced url, timestamp to file
    # get GPS information for starting point from mobile-network, write to file
    # reverse geolocate lat/long to address and write to file
    # traceroute and write to file
    with open("trace_client.txt", "a") as tracer:
        tracer.write("\ntraced url: {} \n".format(trace_url))
        tracer.write("tracer start timestamp: {} \n".format(datetime.now()))
        # stdout = Popen('termux-location -p network', shell=True, stdout=PIPE).stdout
        # output = stdout.read()
        # gps = output.decode()
        # output = gps.split()
        # for item in range(len(output)):
            # output[item] = output[item].replace(',', '').strip()
        # print(output[2])
        tracer.write("latitude: {} \n".format("none"))
        tracer.write("longitude: {} \n".format("none"))
        # geolocator = Nominatim(user_agent="myapp")
        # lat_long = output[2] + ", " + output[4]
        # real_address = geolocator.reverse(lat_long)
        # print(real_address)
        # tracer.write("trace start address: {} \n".format(real_address))
        # wifi_network = subprocess.run("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep SSID'", shell=True, stdout=tracer)
        # tracer.write("tracer wifi-network: {} \n".format(wifi_network))
        time.sleep(0.5)
    with open("trace_client.txt", "a") as tracer:
        subprocess.run('traceroute "{}"'.format(url_ip), shell=True, stdout=tracer)
        time.sleep(0.5)

def temp_data(trace_url):
    # read data from file into dictionary
    keys = {}
    data_trace[trace_url] = keys
    ip_address = []
    line_gps = []

    # clean up txt file
    with open("trace_client.txt", "r+") as tracer:
        d = tracer.readlines()
        tracer.seek(0)
        for line in d:
            if line.strip():
                if "*" not in line:
                    if " 1 " not in line:
                        if line[1].isalpha():
                            tracer.write(line)
                        else:
                            cut_line = line[2:].strip()
                            if cut_line[0] is not "1":
                                tracer.write(cut_line + "\n")
        tracer.truncate()

    # store values in dict
    with open("trace_client.txt", "r+") as tracer:
        for line in tracer:
            line_list = line.split()
            if len(line_list) >= 3:
                if 'timestamp:' in line_list:
                    line_timestamp = [
                        line_list[line_list.index('timestamp:') + 1],
                        line_list[line_list.index('timestamp:') + 2]
                        ]
                    data_trace[trace_url]['timestamp'] = line_timestamp
                if 'latitude:' in line_list:
                    line_gps.append(line_list[line_list.index('latitude:') + 1])
                    data_trace[trace_url]['gps_location_start'] = line_gps
                if 'longitude:' in line_list:
                    line_gps.append(line_list[line_list.index('longitude:') + 1])
                    data_trace[trace_url]['gps_location_start'] = line_gps
                if 'trace start address:' in line_list:
                    line_address = ", ".join(line_list)
                    line_address.replace("trace start address: ", "")
                    data_trace[trace_url]['trace_start_address'] = line_address
                if line_list[1][0] == '(':
                    ip_address.append((line_list[1].strip(')')).strip('('))
                    data_trace[trace_url]['ip_address'] = ip_address
                    # print(ip_address)
    return data_trace

def geo_loc(trace_url, data_trace):
    server_city_country = []
    isp = []
    coordinates = []
    for item in data_trace[trace_url]['ip_address']:
        token = "your token goes here"
        stdout = Popen('curl ipinfo.io/{}?{}'.format(item, token), shell=True, stdout=PIPE).stdout
        output = stdout.read()
        ip_info = json.loads(output.decode())
        try:
            city = ip_info['city']
            if len(city) == 0:
                city = "unknown"
        except KeyError:
            city = "unkown"
        try:
            country = ip_info['country']
        except KeyError:
            country = "unknown"
        location = city + " / " + country
        server_city_country.append(location)
        data_trace[trace_url]['server_city_country'] = server_city_country
        try:
            isp_provider = ip_info['org']
            if len(isp_provider) == 0:
                isp_provider = "unknown"
        except KeyError:
            isp_provider = "unknown"
        isp.append(isp_provider)
        data_trace[trace_url]['isp'] = isp
        try:
            lat_long = ip_info['loc']
        except KeyError:
            lat_long = "unknown"
        coordinates.append(lat_long)
        data_trace[trace_url]['coordinates'] = coordinates
    return data_trace


def print_report(data_trace):
    with open('traceroute_{}.txt'.format(network_name), 'a') as file:
        file.write(json.dumps(data_trace))

def main():
    traceroutes = ['ouiouioui.space', 'nts.live', 'home.nyu.edu']
    for trace_url in traceroutes:
        time.sleep(1)
        url_ip = get_ip(trace_url)
        traceroute(url_ip, trace_url)
        data = temp_data(trace_url)
        geo_ip = geo_loc(trace_url, data)
    print_report(geo_ip)

if __name__ == "__main__":
    main()
