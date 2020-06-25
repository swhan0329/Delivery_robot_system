

import numpy as np
from WSClientAPI import deleteAllOrders, generateRandomOrders
deleteAllOrders()
generateRandomOrders(orders_per_interval=4, default=False)


################################################

#
# # from route_FIFO_0130 import RouteDecision
# from route_Priority_0206 import RouteDecision
# from decision_utils import makeFullyConnectedGraph
# path, cost = makeFullyConnectedGraph()
#
# routeDecision = RouteDecision(path, cost)
#
#
# ################################################
#
#
# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)
#
# print('======')
#
# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr))
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)
#
# print('======')
#
# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)
#
# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr))
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)
#
# print('======')
#
# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)
#
# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr))
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)
#
# print('======')
#
# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)
#
# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr))
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)
#
# print('======')
#
# #############################
# # Priority
#
# # 1. Get all pending orders
#
# # 2. Filter out orders that exceed the robot's load capacity
#
# # 3. Assign priority scores (num_box_weight & distance_weight)
#
# # 4. Sort the orders
#
# # 5. Repeat from 2 to 5


