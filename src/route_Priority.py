import numpy as np
import time 
import datetime

from WSClientAPI import retrievePendingOrders_all, retrieveFilledOrders, markOrderFilled, retrievePendingOrders_id
from decision_utils import address_validator
# path, cost = makeFullyConnectedGraph()


##############################################################################
## TEST ##
import pdb
# deleteAllOrders()
# generateRandomOrders(orders_per_interval=5, boxes_per_order=5, default=True)
##############################################################################



# location = ['stop', '101', '102', '103', '201', '202', '203']


# _0 => counter-clockwise
# _1 => clockwise


class RouteDecision():
    def __init__(self, path, cost, weight_dist = 1, weight_box = 0.5,  max_load=20, delivery_threshold=10):

        self.start_loc = 'stop_0' # start at STOP counter clockwise direction !!!!!!!

        self.path = path
        self.cost = cost

        self.weight_dist = weight_dist
        self.weight_box = weight_box

        self.max_load = max_load

        self.threshold = delivery_threshold
        self.path_flag = False

        self.invalid_orders = []
        # self.ordersToDeliver = []

        # original_orders = pending_orders + partially_delivered
        self.original_orders = {} # original order
        self.pending_orders = {} # what we want to deliver
        self.partially_delivered = {} # what we have delivered

        self.address2orderid = {}
        self.orderid2address = {}

        # inventory
        self.inventory_red = 26
        self.inventory_blue = 26
        self.inventory_green = 27

        self.num_pending_orders = 0 
        self.num_completed_orders = 0   
        self.start_time = time.time()   
        self.cum_orders = 0     
        self.DeliveryTime = [] # 평균 delivery time   


    def getCurrentOrdersPending(self): # 남은 오더  
        response = retrievePendingOrders_all()  
        self.num_pending_orders = len(response) - len(self.invalid_orders)  
        return self.num_pending_orders  


    def getNumCompletedOrders(self): # 배달한 오더   
        return self.num_completed_orders    


    def getNumTotalOrders(self): # 총 누적 오더  
        self.cum_orders = self.num_completed_orders + self.num_pending_orders   
        return self.cum_orders  


    def getAllDeliveryTime(self):   
        return self.DeliveryTime


    def getInvalidOrders(self):
        return self.invalid_orders


    def generate_route(self, start_loc, end_loc, print_route=False):
        i = np.argmin([self.cost[(start_loc, end_loc+'_0')], self.cost[(start_loc, end_loc+'_1')]])

        route_cost = self.cost[(start_loc, end_loc+'_'+str(i))]
        current_route = self.path[(start_loc, end_loc+'_'+str(i))]

        if current_route==None:
            current_route = [start_loc, start_loc]

            if print_route:
                print('Delivery Route:',start_loc.replace('_0', '_cc').replace('_1', '_c'), end = ' ')
                print('=>', start_loc.replace('_0', '_cc').replace('_1', '_c'), end = ' ')
        else:
            if print_route:
                print('Delivery Route:',start_loc.replace('_0', '_cc').replace('_1', '_c'), end = ' ')
                for loc in current_route[1:]:
                    print('=>', loc.replace('_0', '_cc').replace('_1', '_c'), end = ' ')
                print('')

        return current_route, route_cost, end_loc+'_'+str(i)


    def update_inventory(self, red=1, blue=1, green=1):
        self.inventory_red += red
        self.inventory_blue = blue
        self.inventory_green = green


    def getInventory(self):
        return np.array([self.inventory_red, self.inventory_blue, self.inventory_green])


    def checkInventoryReplenish(self, num_box_threshold = 5):
        flag = self.getInventory() >= num_box_threshold
        return flag.tolist()


    def order_log(self):
        pass


    def sort_location(self, start, candidate):
        goals = []
        cost_list = []
        directions = []
        for c in candidate:
            i = np.argmin([self.cost[(start, c+'_0')], self.cost[(start, c+'_1')]])
            direction = ['_0', '_1'][i]
            if c != start:
                goals.append(c)
                cost_list.append(self.cost[(start, c+direction)])
                directions.append(direction)
        goals = np.array(goals)
        directions = np.array(directions)
        return goals[np.argsort(cost_list)][0], directions[np.argsort(cost_list)][0]


    def getAction(self, delivery_path, delivery_boxes, order_ids):
        # print("getAction:", delivery_path, delivery_boxes, order_ids)
        actions = []
        boxes = []
        info = []
        past_goal = None

        for path, box, id_ in zip(delivery_path[:-1], delivery_boxes, order_ids):
            action = path[-1][path[-1].index('_')+1:].replace('0', 'cc').replace('1', 'c')
            goal = path[-1][:path[-1].index('_')]
            sub_info = [[id_]+box]

            if past_goal == goal:
                boxes[-1] += np.array(box)
                info[-1].extend(sub_info)
            else:
                actions.append([action, goal])
                boxes.append(np.array(box))
                info.append(sub_info)

            past_goal = goal

        action = delivery_path[-1][-1][delivery_path[-1][-1].index('_')+1:].replace('0', 'cc').replace('1', 'c')
        goal = delivery_path[-1][-1][:delivery_path[-1][-1].index('_')]
        actions.append([action, goal])

        return actions, [[a[1]]+b.tolist() for a, b in zip(actions[:-1], boxes)], info


    def getOrdersInfo(self, res):
        '''
        returns order_id, address, boxes]
        '''
        order_id = res['id']
        address = str(res['address'])

        num_boxes = np.array([res['red'], res['blue'], res['green']])
        return order_id, address, num_boxes


    def isSameBox(self, A, B):
        if A[0]==B[0] and A[1]==B[1] and A[2]==B[2]:
            return True
        else:
            return False


    def checkOrderFullfilled(self, package_by_addr):
        # JDY
        for order_id, red, blue, green in package_by_addr:
            package = np.array([red, blue, green])

            # remove pending order if delivery is done
            if order_id in self.original_orders.keys():

                # check fullfilled in the first time
                if self.isSameBox(package, self.original_orders[order_id]):
                    del self.original_orders[order_id]
                    del self.pending_orders[order_id]

                    address = self.orderid2address[order_id]
                    del self.orderid2address[order_id]
                    self.address2orderid[address].remove(order_id)

                    orderdate = retrievePendingOrders_id(str(order_id))[0]['orderdate'] 
                    orderdate = datetime.datetime.strptime(orderdate, "%Y-%m-%dT%H:%M:%S.000Z") 
                    now = datetime.datetime.now()   
                    time_diff = now - orderdate 
                    time_diff_in_sec = time_diff.total_seconds() + 3600*5   
                    self.DeliveryTime.append(time_diff_in_sec)  
                    markOrderFilled(str(order_id))  
                    self.num_completed_orders += 1

                # check filled in not the first time
                elif order_id in self.partially_delivered.keys() and self.isSameBox(package+self.partially_delivered[order_id], self.original_orders[order_id]):
                    del self.original_orders[order_id]
                    del self.pending_orders[order_id]
                    del self.partially_delivered[order_id]

                    address = self.orderid2address[order_id]
                    del self.orderid2address[order_id]
                    self.address2orderid[address].remove(order_id)

                    orderdate = retrievePendingOrders_id(str(order_id))[0]['orderdate'] 
                    orderdate = datetime.datetime.strptime(orderdate, "%Y-%m-%dT%H:%M:%S.000Z") 
                    now = datetime.datetime.now()   
                    time_diff = now - orderdate 
                    time_diff_in_sec = time_diff.total_seconds() + 3600*5   
                    self.DeliveryTime.append(time_diff_in_sec)  
                    markOrderFilled(str(order_id))  
                    self.num_completed_orders += 1

                # not filled thus save it in partially_delivered
                else:
                    if order_id in self.partially_delivered.keys():
                        self.partially_delivered[order_id] += package
                    else:
                        self.partially_delivered[order_id] = package

            else:
                import pdb; pdb.set_trace()


    def get_all_box_num(self, response):
        num_boxes = 0
        for res in response:
            num_boxes += (res['red'] + res['blue'] + res['green'])
        return num_boxes


    def getDeliveryDecision(self, response):
        if self.get_all_box_num(response) >= self.threshold:
        # if len(response) > self.threshold:
            return True
        else:
            return False

    def calculate_distance(self, start_loc, end_address):
        # JDY
        end_loc = end_address+'_0'
        cost = self.cost[(start_loc, end_loc)]
        if cost > self.cost[(start_loc, end_address + '_1')]:
            cost = self.cost[(start_loc, end_address + '_1')]
            end_loc = end_address + '_1'
        return cost, end_loc

    def current_order_state(self, id_list, current_loc, current_load):
        # JDY
        current_possible_order_ids = []
        current_possible_boxes = []
        current_possible_distance = []
        current_possible_loc = []
        current_partial_order_ids = []
        current_partial_boxes = []
        current_partial_distance = []
        current_partial_loc = []
        for order_id, boxes_item in self.pending_orders.items():
            if order_id not in id_list:
                #print("order:", order_id, "address:", self.orderid2address[order_id], "box:", boxes_item )
                total_boxes = np.sum(boxes_item)
                curr_dist, next_loc = self.calculate_distance(current_loc, self.orderid2address[order_id])
                if self.max_load - current_load >= total_boxes:
                    current_possible_order_ids.append(order_id)
                    current_possible_boxes.append(total_boxes)
                    current_possible_distance.append(curr_dist)
                    current_possible_loc.append(next_loc)
                else:
                    current_partial_order_ids.append(order_id)
                    current_partial_boxes.append(total_boxes)
                    current_partial_distance.append(curr_dist)
                    current_partial_loc.append(next_loc)

        return current_possible_order_ids, current_possible_boxes, current_possible_distance, current_possible_loc, \
               current_partial_order_ids, current_partial_boxes, current_partial_distance, current_partial_loc

    def calculate_priority(self, current_load, current_possible_order_ids, current_possible_boxes, current_possible_distance, current_possible_loc,
               current_partial_order_ids, current_partial_boxes, current_partial_distance, current_partial_loc):
        # JDY

        possible_score_idx = None
        if len(current_possible_order_ids) > 0:
            current_possible_boxes_np = np.array(current_possible_boxes)
            current_possible_distance_np = np.array(current_possible_distance)
            current_possible_score = self.weight_dist * current_possible_distance_np \
                                     + self.weight_box * current_possible_boxes_np
            possible_score_idx = np.argmin(current_possible_score)

        partial_score_idx = None
        if len(current_partial_order_ids) > 0:
            current_partial_boxes_np = np.array(current_partial_boxes)
            current_partial_distance_np = np.array(current_partial_distance)
            current_partial_score = self.weight_dist * current_partial_distance_np \
                                    + self.weight_box * (self.max_load - current_load) \
                                    + current_partial_boxes_np / (self.max_load - current_load)
            partial_score_idx = np.argmin(current_partial_score)

        if possible_score_idx != None and partial_score_idx != None:
            if current_possible_score[possible_score_idx] <= current_partial_score[partial_score_idx]:
                return possible_score_idx, "possible"
            else:
                return partial_score_idx, "partial"
        elif possible_score_idx != None and partial_score_idx == None:
            return possible_score_idx, "possible"
        elif possible_score_idx == None and partial_score_idx != None:
            return partial_score_idx, "partial"
        else:
            return None, None

    def execute(self, print_route=False, mode='prior'):

        #
        # 103         203
        #
        # 102         202
        #
        # 101         201
        #
        #       stop

        # 0: counterclock-wise
        # 1: clockwise

        # If the same address but different orderID, we add all the boxes
        # but remember what boxes belong to what orders

        '''
        [True/False, # start or not start
        [[cc, 201], [cc, 202], [c, stop]], # path for each round
        [[1,2,0],[1,0,0]]] # boxes for each location for each round || [red, blue, green]
        '''

        response = retrievePendingOrders_all()

        # If no pending orders, output empty decision
        if len(response) == 0 or len(response)==len(self.invalid_orders):
            return [False, [], [], []]


        # Check Delivery Start Threshold
        self.path_flag = self.getDeliveryDecision(response) # True / False


        loading_capacity_exeeded = False


        load_capacity = self.max_load


        # collect pending orders
        for res in response:
            order_id, address, boxes = self.getOrdersInfo(res) # str, str, [r, b, g]
            # print("response", order_id, address, boxes, res)
            # print("partial", self.partially_delivered, self.partially_delivered.keys())
            # order validation
            if address_validator(address)==False:
                self.invalid_orders[order_id] = [address, boxes]
                if print_route:
                    print('Invalid order detected')
                    print('Order_id:', order_id, '| Address:', address, '| Boxes:', boxes)
                    print()
                continue # this does not add orders to address2orderid & pending_orders

            self.original_orders[order_id] = boxes.copy() # [r, b, g]

            # Define address2orderid & orderid2address
            if address in self.address2orderid.keys():
                self.address2orderid[address].add(order_id)
            else:
                self.address2orderid[address] = {order_id}
            self.orderid2address[order_id] = address
            
            # Declare orders for partial delivery
            if order_id in self.partially_delivered.keys():
                # print("done", boxes, self.partially_delivered[order_id])
                boxes -= self.partially_delivered[order_id]
            self.pending_orders[order_id] = boxes

        if mode == "prior":
            # Delivery decision
            if len(self.pending_orders)>0: # we have at least one order to deliver
                # print(self.pending_orders)
                current_loc = self.start_loc
                current_inventory = self.getInventory().copy()
                id_list = []
                loc_list = []
                path_list = []
                box_list = []
                current_load = 0
                while current_load < self.max_load:
                    current_possible_order_ids, current_possible_boxes, current_possible_distance, current_possible_loc, \
                    current_partial_order_ids, current_partial_boxes, current_partial_distance, current_partial_loc = self.current_order_state(id_list, current_loc, current_load)
                    # print(current_possible_order_ids, current_possible_distance, current_possible_loc)
                    # print(current_partial_distance)
                    score_idx, flag_possible = self.calculate_priority(current_load, current_possible_order_ids, current_possible_boxes, current_possible_distance, current_possible_loc,
                                                      current_partial_order_ids, current_partial_boxes, current_partial_distance, current_partial_loc)
                    if flag_possible == "possible":
                        next_order_id = current_possible_order_ids[score_idx]
                        next_loc = current_possible_loc[score_idx]
                        next_path = self.path[(current_loc, next_loc)]
                        if next_path != None:
                            path_list.append(self.path[(current_loc, next_loc)])
                        else:
                            path_list.append([current_loc, current_loc])
                        current_loc = next_loc
                        current_load += current_possible_boxes[score_idx]

                        loc_list.append(current_loc)
                        temp_boxes = self.pending_orders[next_order_id]
                        current_inventory -= temp_boxes
                        box_list.append(list(temp_boxes))
                        id_list.append(next_order_id)
                    elif flag_possible == "partial":
                        temp_delivery_box = self.max_load - current_load
                        next_order_id = current_partial_order_ids[score_idx]
                        next_loc = current_partial_loc[score_idx]
                        next_path = self.path[(current_loc, next_loc)]
                        if next_path != None:
                            path_list.append(self.path[(current_loc, next_loc)])
                        else:
                            path_list.append([current_loc, current_loc])
                        current_loc = next_loc
                        current_load += current_partial_boxes[score_idx]
                        loc_list.append(current_loc)
                        temp_boxes = self.pending_orders[next_order_id].copy()
                        id_list.append(next_order_id)

                        package = np.array([0, 0, 0])
                        temp_number_load = 0
                        while True:
                            box_idx = np.argsort(current_inventory)[::-1]
                            find = False
                            for idx in box_idx:
                                if temp_boxes[idx] > 0:
                                    temp_boxes[idx] -= 1
                                    current_inventory[idx] -= 1
                                    package[idx] += 1
                                    temp_number_load += 1
                                    if temp_number_load == temp_delivery_box:
                                        find = True
                                        break
                                    if sum(temp_boxes) == 0:
                                        find = True
                                        break
                            if find:
                                break
                        box_list.append(list(package))
                    else:
                        break
                if len(path_list) > 0:
                    current_route, route_cost, end_loc = self.generate_route(current_loc, 'stop')
                    path_list.append(current_route)
                # print("path_list:", path_list)
                goal_and_action, delivery_boxes_by_addr, delivery_info_by_addr = self.getAction(path_list, box_list, id_list)

            return [self.path_flag, goal_and_action, delivery_boxes_by_addr, delivery_info_by_addr]

        elif mode == 'FIFO':

            # Delivery decision
            if len(self.pending_orders)>0: # we have at least one order to deliver

                order_ids = []
                delivery_path = []
                delivery_boxes = []

                address_to_visit = []
                basket = {}

                for order_id in sorted(self.pending_orders.keys()): # sort by order_id

                    if loading_capacity_exeeded:
                        break

                    package = np.array([0,0,0])
                    address = self.orderid2address[order_id]                
                    orders = self.pending_orders[order_id].copy()

                    while True:
                        box_idx = np.argsort(self.getInventory())[::-1]
                        find = False 
                        for idx in box_idx:
                            if orders[idx] > 0:
                                orders[idx] -= 1
                                package[idx] += 1
                                load_capacity -= 1
                                if load_capacity == 0:
                                    loading_capacity_exeeded = True
                                    find = True 
                                    break
                                if sum(orders) == 0:
                                    find = True 
                                    break
                        if find:
                            break 

                    address_to_visit.append(address)
                    if address in basket.keys():
                        basket[address].append([package, order_id])                    
                    else:
                        basket[address] = [[package, order_id]]                    

                # Given selected orders, get delivery path decision
                address_to_visit_sorted = []
                start_loc = self.start_loc
                while len(address_to_visit) > 0:
                    next_loc, next_dir = self.sort_location(start_loc, address_to_visit)
                    address_to_visit_sorted.append(next_loc)
                    address_to_visit.remove(next_loc)
                    start_loc = next_loc+next_dir

                if print_route:
                    print('###address_to_visit:', address_to_visit_sorted)
                    print('###order_ids:', order_ids)
                    print('############################')

                for address in address_to_visit_sorted: # address can be the same

                    end_loc = address
                    current_route, route_cost, end_loc = self.generate_route(self.start_loc, end_loc, print_route=print_route)
                    delivery_path.append(current_route)
                    package, order_id = basket[address].pop(0)
                    delivery_boxes.append(package.tolist())
                    order_ids.append(order_id)

                    self.start_loc = end_loc

                end_loc = 'stop'
                current_route, route_cost, end_loc = self.generate_route(self.start_loc, end_loc)
                delivery_path.append(current_route)
                self.start_loc = end_loc        

            if print_route:
                print('Path route:')
                print(delivery_path, delivery_boxes, order_ids)
                print()

            goal_and_action, delivery_boxes_by_addr, delivery_info_by_addr = self.getAction(delivery_path, delivery_boxes, order_ids)
            return [self.path_flag, goal_and_action, delivery_boxes_by_addr, delivery_info_by_addr]

        else:

            raise ValueError("Unknown decision strategy type {:s}.".format(mode))


            
