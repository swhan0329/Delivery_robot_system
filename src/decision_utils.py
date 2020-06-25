# import WSClientAPI as api
import heapq


# dist = {('stop_0', '101_0'): 4, ('101_1', 'stop_1'): 4,
#         ('101_0', '102_0'): 2, ('102_1', '101_1'): 2,
#         ('102_0', '103_0'): 2, ('103_1', '102_1'): 2,
#         ('103_0', '203_0'): 4, ('203_1', '103_1'): 4,
#         ('202_1', '203_1'): 2, ('203_0', '202_0'): 2,
#         ('201_1', '202_1'): 2, ('202_0', '201_0'): 2,
#         ('201_0', 'stop_0'): 4, ('stop_1', '201_1'): 4,
#         ('stop_0', 'stop_1'): 2, ('stop_1', 'stop_0'): 2,
#         ('101_0', '101_1'): 2, ('101_1', '101_0'): 2,
#         ('102_0', '102_1'): 2, ('102_1', '102_0'): 2,
#         ('103_0', '103_1'): 2, ('103_1', '103_0'): 2,
#         ('201_0', '201_1'): 2, ('201_1', '201_0'): 2,
#         ('202_0', '202_1'): 2, ('202_1', '202_0'): 2,
#         ('203_0', '203_1'): 2, ('203_1', '203_0'): 2
#         }

dist_to_stop = 100
dist_from_stop = 2
U_line = 2
U_corner = 100
dist_100 = 2
dist_200 = 2
dist_100_200 = 2

dist = {('stop_0', '101_0'): dist_from_stop, ('101_1', 'stop_1'): dist_to_stop,
        ('101_0', '102_0'): dist_100, ('102_1', '101_1'): dist_100,
        ('102_0', '103_0'): dist_100, ('103_1', '102_1'): dist_100,
        ('103_0', '203_0'): dist_100_200, ('203_1', '103_1'): dist_100_200,
        ('202_1', '203_1'): dist_200, ('203_0', '202_0'): dist_200,
        ('201_1', '202_1'): dist_200, ('202_0', '201_0'): dist_200,
        ('201_0', 'stop_0'): dist_to_stop, ('stop_1', '201_1'): dist_from_stop,
        ('stop_0', 'stop_1'): U_corner, ('stop_1', 'stop_0'): U_corner,
        ('101_0', '101_1'): U_corner, ('101_1', '101_0'): U_corner,
        ('102_0', '102_1'): U_line, ('102_1', '102_0'): U_line,
        ('103_0', '103_1'): U_corner, ('103_1', '103_0'): U_corner,
        ('201_0', '201_1'): U_corner, ('201_1', '201_0'): U_corner,
        ('202_0', '202_1'): U_line, ('202_1', '202_0'): U_line,
        ('203_0', '203_1'): U_corner, ('203_1', '203_0'): U_corner
        }

adj = {'stop_0': ['101_0', 'stop_1'],
        'stop_1': ['201_1', 'stop_0'],
        '101_0': ['101_1', '102_0'],
        '101_1': ['101_0', 'stop_1'],
        '102_0': ['102_1', '103_0'],
        '102_1': ['102_0', '101_1'],
        '103_0': ['103_1', '203_0'],
        '103_1': ['103_0', '102_1'],
        '201_0': ['stop_0', '201_1'],
        '201_1': ['202_1', '201_0'],
        '202_0': ['202_1', '201_0'],
        '202_1': ['202_0', '203_1'],
        '203_0': ['203_1', '202_0'],
        '203_1': ['203_0', '103_1'],
       }

node = ['stop_0', '101_0', '102_0', '103_0', '201_0', '202_0', '203_0',
        'stop_1', '101_1', '102_1', '103_1', '201_1', '202_1', '203_1']
for address in node:
    dist[(address, address)] = 0

def address_validator(address):
    for add in node:
        add = add.replace('_0', '').replace('_1', '')
        if address == add:
            return True
    return False


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

def uniformCostSearch(start, end):
    '''
    :param start: start node
    :param end: end node
    :return: path, cast
    '''
    if (start not in node) or (end not in node):
        print("start or end node is invaild")
        return None, 0

    if start == end:
        return None, 0

    if start != end:
        Succ_queue = PriorityQueue()
        Visited = [start]
        Parents = {start: {}}
        now_cost = 0
        priority = dict()

        curr_pt = start
        while (1):

            # Make Successors
            Successors = adj[curr_pt]
            for succ in Successors:
                if (succ not in Visited) and (succ not in priority):
                    Succ_queue.update([succ, now_cost + dist[(curr_pt, succ)]], now_cost + dist[(curr_pt, succ)])
                    Parents[succ] = curr_pt
                    priority[succ] = now_cost + dist[(curr_pt, succ)]
                if (succ in priority):
                    if priority[succ] > now_cost + dist[(curr_pt, succ)]:
                        priority[succ] = now_cost + dist[(curr_pt, succ)]
                        Succ_queue.update([succ, now_cost + dist[(curr_pt, succ)]], now_cost + dist[(curr_pt, succ)])
                        Parents[succ] = curr_pt

            # Expand next node
            while not Succ_queue.isEmpty():
                next = Succ_queue.pop()
                try:
                    del priority[next[0]]
                except:
                    pass
                if not (next[0] in Visited) and (next[0] not in priority):
                    curr_pt = next[0]
                    Visited.append(next[0])
                    now_cost = next[1]
                    break

            # Goal Test
            if curr_pt == end:
                break

        # Extract node
        path = [curr_pt]
        while Parents[path[-1]] != {}:
            path.append(Parents[path[-1]])
        path.reverse()
        return path, now_cost

def makeFullyConnectedGraph():

    cost = dict()
    path = dict()
    for start in node:
        for end in node:
            p,c = uniformCostSearch(start, end)
            cost[(start, end)] = c
            path[(start, end)] = p

    return path, cost

# print(uniformCostSearch('102_0', '202_0'))
# print(uniformCostSearch('102_0', '202_1'))
# print(uniformCostSearch('102_1', '202_0'))
# print(uniformCostSearch('102_1', '202_1'))

# path, cost = makeFullyConnectedGraph()
# print("path:", path)
# print("cost:", cost)
