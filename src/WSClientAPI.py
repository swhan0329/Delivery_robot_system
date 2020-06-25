import numpy as np
import time

import urllib.request
import json
import pdb

ip_address = "localhost:3000"

def retrievePendingOrders_all():

    url = "http://" + ip_address + "/api/pending"

    inputLine = urllib.request.urlopen(url)
    inputLine = json.loads(inputLine.read().decode())
    response = []
    for line in inputLine["Orders"]:
        response.append(line)
    #     print("PendingOrder", line)
    return response

def retrievePendingOrders_id(id):

    url = "http://" + ip_address + "/api/pending/" + id

    inputLine = urllib.request.urlopen(url)
    inputLine = json.loads(inputLine.read().decode())

    response = inputLine["Users"]
    return response

def retrievePendingOrders_customer(customer):

    url = "http://" + ip_address + "/api/pendingcustorders/" + customer

    inputLine = urllib.request.urlopen(url)
    inputLine = json.loads(inputLine.read().decode())
    response = inputLine["Users"]

    return response

def retrieveFilledOrders():

    url = "http://" + ip_address + "/api/filled"

    inputLine = urllib.request.urlopen(url)
    inputLine = json.loads(inputLine.read().decode())

    response = inputLine["Orders"]
    return response

def retrieveFilledOrders_customer(customer):
    # we need to check this method later.
    url = "http://" + ip_address + "/api/filled"

    inputLine = urllib.request.urlopen(url)
    inputLine = json.loads(inputLine.read().decode())

    response = inputLine["Orders"]

    return response

def newOrder(customer, red, blue, green, custaddress):

    url = "http://" + ip_address + "/api/neworder"

    input_ = "&customer="+customer+"&red="+red+"&blue="+blue+"&green="+green+"&address="+custaddress

    inputLine = urllib.request.urlopen(url, data=input_.encode())
    inputLine = json.loads(inputLine.read().decode())

def deleteOrder(id):

    url = "http://" + ip_address + "/api/deleteOrder/" + id

    req = urllib.request.Request(url, method="DELETE")
    response = urllib.request.urlopen(req)

def markOrderFilled(id):

    url = "http://" + ip_address + "/api/markOrderFilled/" + id
    req = urllib.request.Request(url, method="POST")

    inputLine = urllib.request.urlopen(req)
    inputLine = json.loads(inputLine.read().decode())

    response = inputLine
    return response

def deleteAllOrders():
    response = retrievePendingOrders_all()
    for r in response:
        deleteOrder(str(r['id']))

    response = retrieveFilledOrders()
    for r in response:
        deleteOrder(str(r['id']))

def generateInterArrival(T = 1200, lamb = 1/6, lamb_t = 1/6):
    t = 0
    k = 0
    event_time = []
    while t < T:
        r = np.random.uniform(0, 1)
        t = t - np.log(r) / lamb
        if t > T:
            break
        s = np.random.uniform(0, 1)
        if s <= (lamb_t / lamb):
            k = k + 1
            event_time.append(t)

    return event_time

def generateRandomOrders(orders_per_interval=3, default=False):
    box_colors_num = 3
    address = ['101', '102', '103', '203', '202', '201']
    # address = ['101', '102', '999']

    # 1200 sec / 200 oroders

    if default:

        for add in address:
            customer = 'generated_customer'
            red, blue, green = np.random.randint(10, size=box_colors_num)        
            newOrder(customer, str(red), str(blue), str(green), add)   

    else:

        add = np.random.randint(len(address), size=orders_per_interval)

        for idx in add:
            custaddress = address[idx]
            customer = 'generated_customer'
            red, blue, green = np.random.randint(10, size=box_colors_num)        
            newOrder(customer, str(red), str(blue), str(green), custaddress)


def generateSequentialRandomOrders(max_min = 1):
    box_colors_num = 3
    address = ['101', '102', '103', '203', '202', '201']
    # address = ['101', '102', '999']

    # time_intervals = generateInterArrival()
    # orders_per_interval = 1

    # for interval in time_intervals:
    #     print('Interval:', interval)

    #     add = np.random.randint(len(address), size=orders_per_interval)

    #     for idx in add:
    #         custaddress = address[idx]
    #         customer = 'generated_customer'
    #         red, blue, green = np.random.randint(10, size=box_colors_num)        
    #         newOrder(customer, str(red), str(blue), str(green), custaddress)

    #     time.sleep(interval)

    start_time = time.time()
    max_order_time = max_min*60
    while (time.time() - start_time) < max_order_time:

        bulk = np.random.binomial(1, p=0.03)+1 # Bulk 97% 1 orders | 3% 2 orders
        print('bulk:', bulk)
        add = np.random.randint(len(address), size=bulk)
        interval =  np.random.uniform(0, 30) # interval uniform 0 - 30
        print('interval:', interval)

        for idx in add:
            custaddress = address[idx]
            customer = 'generated_customer'
            red, blue, green = np.random.randint(10, size=box_colors_num)        
            newOrder(customer, str(red), str(blue), str(green), custaddress)

        time.sleep(interval)    

