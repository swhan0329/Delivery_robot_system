

import numpy as np
from WSClientAPI import deleteAllOrders, generateRandomOrders, generateSequentialRandomOrders
deleteAllOrders()
# generateRandomOrders(orders_per_interval=10, default=False)
generateSequentialRandomOrders(min=20)

################################################


# from route_Priority_0206 import RouteDecision
# from decision_utils import makeFullyConnectedGraph
# path, cost = makeFullyConnectedGraph()

# routeDecision = RouteDecision(path, cost)


################################################


# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addsr = routeDecision.execute(print_route=False)

# print('======')

# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr)) 
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)

# print('======')

# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)

# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr)) 
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)

# print('======')

# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)

# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr)) 
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)

# print('======')

# flag, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = routeDecision.execute(print_route=False)

# print('flag:', flag)
# print('delivery_path:', delivery_path)
# print('delivery_boxes_by_addr:', delivery_boxes_by_addr)
# print('delivery_info_by_addr:', delivery_info_by_addr)
# print('len(delivery_info_by_addr):', len(delivery_info_by_addr)) 
# for i, d in enumerate(delivery_info_by_addr):
# 	routeDecision.checkOrderFullfilled(delivery_info_by_addr[i])
# print('#####', routeDecision.partially_delivered)

# print('======')
