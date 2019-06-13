# version from 5/6/2019 1:05 am
import requests
import json
import time
import os
import datetime

# interval between measurements in seconds
interval = 2
# definiton of connectors in nodeid:connectorid format
connectors = (
              {1:1},
              {1:2},
              {1:3},
              {2:1},
              {2:2},
              {3:1},
              {3:2},
              {4:1},
              {4:2},
              {4:3},
              {5:1},
              {5:2},
              {6:1},
              {6:2},
              )

# function to generate url for API requests based on opeational data store
# and connector number (node and connector ids)
def generate_url(nodeid, connectorid):
    restconf_url = 'http://192.168.56.101:8181/restconf/'
    inventory_url = 'operational/opendaylight-inventory:nodes/'
    # node/{id}/ e.g. node/openflow:1/
    node_url = 'node/'
    nodename = 'openflow:'
    nodeid_url = nodename + str(nodeid) + '/'
    # node-connector/{id}/ e.g. node-connector/openflow:1:1/
    connector_url = 'node-connector/'
    connectorid_url = nodename + str(nodeid) +':' + str(connectorid) + '/'
    statistics_url = ('opendaylight-port-statistics:'
                      'flow-capable-node-connector-statistics/')
    packets_url = 'packets/'
    url  = (restconf_url + inventory_url + node_url + nodeid_url +
            connector_url + connectorid_url + statistics_url + packets_url)
    # returns generated URL
    return(url)

# function to retrieve packet counts from a connector (port)
def get_packets(node, connector):
    # genrates url based on connector
    url = generate_url(node, connector)
    # retrieves XML data
    response = requests.get(url, auth=('admin', 'admin'))
    # converts XML data to JSON data (dictionary)
    response_json = response.json()
    # extracts rx and tx count from converted dictionary
    rx = response_json["opendaylight-port-statistics:packets"]["received"]
    tx = response_json["opendaylight-port-statistics:packets"]["transmitted"]
    # returns received and transmitted packets from a connector
    return rx, tx

# generates output print line based on imput parameter
def generate_line(type):
    # definition of local variables
    printline = str()
    header_line = str()
    line_rx = str()
    line_tx = str()
    values_rx = {}
    values_tx = {}
    # parsing through manually defined list of tuples (connectors)
    for eachconnector in connectors:
        for node, connector in eachconnector.items():

            # first output line to list connector names
            if type == 'headers':
                connector_name = str(node) + ":" + str(connector)
                header_line = (header_line + "Con:" + " " *
                               (5 - len(str(node)) - len(str(connector))) +
                               connector_name + "|")

            # output lines to show statistics
            elif type == 'packets':
                connector_name = str(node) + ":" + str(connector)
                rx, tx = get_packets(node, connector)
                # creating print output
                line_rx = (line_rx + 'Rx:' + " " * (7 - len(str(rx)))
                           + str(rx) + "|")
                line_tx = (line_tx + 'Tx:' + " " * (7 - len(str(tx)))
                           + str(tx) + "|")
                # saving counts for measurement
                values_rx[connector_name] = rx
                values_tx[connector_name] = tx

            # calculation of packet count difference
            elif type == 'calculate':
                connector_name = str(node) + ":" + str(connector)
                # calculated from global variables
                result_rx = (end_values_rx[connector_name] -
                             start_values_rx[connector_name])
                result_tx = (end_values_tx[connector_name] -
                             start_values_tx[connector_name])
                # adding + sign if change
                if result_rx == 0: result_rx_s = str(result_rx)
                else: result_rx_s = '+' + str(result_rx)
                if result_tx == 0: result_tx_s = str(result_tx)
                else: result_tx_s = '+' + str(result_tx)
                #creating print output
                line_rx = (line_rx + 'Rx:' + " " * (7 - len(result_rx_s)) +
                           result_rx_s+ "|")
                line_tx = (line_tx + 'Tx:' + " " * (7 - len(result_tx_s)) +
                           result_tx_s+ "|")

    # defining print line based on parameter
    if type == 'headers':
        printline = header_line
    elif type == 'packets':
        printline = line_rx + '\n' + line_tx
        # delay between individual readings
        time.sleep(interval)
    elif type == 'calculate':
        printline = line_rx + '\n' + line_tx
    # function return these, called as generate_line('')[i]
    return printline, values_rx, values_tx

# MAIN PROGRAM START
# clearing screen
# os.system('cls')
# title

try:
    print('REST API Controller OVS Connectors Packets Statistics ' +
          'Retrieval Tool')

    readings_note = input ('Enter a note for this reading (or press Enter to ' +
                           'skip) > ')

    #opens a file with results (results appended)
    results_file = open('results.txt', 'a')

    # main program loop - prints headings, measurements and calculate results
    for round in range(0,11):
        if round == 0:
            line = generate_line('headers')[0]
            # defining separators for future use
            line_separator = '-' * len(line)
            line_separator_thick = '=' * len(line)
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')
            print("READINGS")
            results_file.write("READINGS" '\n')
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')
            #prints header and saves for future use
            header_line = line
            print(header_line)
            results_file.write(header_line + '\n')
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')

        elif round == 1:
            # measurements + display + saving first reading
            line, start_values_rx, start_values_tx = generate_line('packets')
            print(line)
            results_file.write(line + '\n')
            print(line_separator)
            results_file.write(line_separator + '\n')

        elif round > 1 and round < 10:
            # measurements + display
            line = generate_line('packets')[0]
            print(line)
            results_file.write(line + '\n')
            print(line_separator)
            results_file.write(line_separator + '\n')

        elif round == 10:
            # measurements + display + saving last reading
            line, end_values_rx, end_values_tx = generate_line('packets')
            print(line)
            results_file.write(line + '\n')
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')
            # printing results
            print("RESULTS")
            results_file.write("RESULTS" + '\n')
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')
            print(header_line)
            results_file.write(header_line + '\n')
            print(line_separator_thick)
            results_file.write(line_separator_thick + '\n')
            # calculating and printing results
            line = generate_line('calculate')[0]
            print(line)
            results_file.write(line + '\n')
            print(line_separator)
            results_file.write(line_separator + '\n')

    results_file.write('Results from: ' + str(datetime.datetime.now()) + ', ' +
                       'interval was: '+ str(interval) + ' second(s), ' +
                       'with a note: ' + readings_note + '\n')
    results_file.write(line_separator_thick + '\n')
    results_file.close()
    # footer
    print('Table shows number of packets received and transmitted')
    print('as returned from the controller counters via REST API.')
    print('Measured in ' + str(interval) + ' second(s) increments.')
    print('\n')

except Exception as ex:
    print('Error in: ',str(ex))
    
# MAIN PROGRAM END
