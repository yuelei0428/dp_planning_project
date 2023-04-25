from utils import *
import math
import heapq
import minigrid

# Left and right is the other way around in the map
MF = 0  # Move Forward
TL = 1  # Turn Left
TR = 2  # Turn Right
PK = 3  # Pickup Key
UD = 4  # Unlock Door

def equal_ignore_order(a, b):
    """ Use only when elements are neither hashable nor sortable! """
    if len(a) != len(b):
        return False
    unmatched = list(b)
    for element in a:
        try:
            unmatched.remove(element)
        except ValueError:
            return False
    return True

def coor_in_list(coor, list):
    for i in range(len(list)):
        if coor[0] == list[i][0] and coor[1] == list[i][1]:
            return True
    return False

# decide whether we should put next into pq given the visited set
def push_next_to_pq(next, visited, pq):
    if next not in visited:
        heapq.heappush(pq, next)
        visited.append(next)
    else:
        for i in range(len(visited)):
            if visited[i] == next:
                if visited[i].cost > next.cost:
                    visited[i].cost = next.cost
                    heapq.heappush(pq, next)

class state:
    def __init__(self, pos, dir, key, unlocked_door=[], opened_door=[], cost=math.inf, prev=None, action=None):
        self.pos = pos
        self.dir = dir
        self.key = key
        self.unlocked_door = unlocked_door
        self.opened_door = opened_door
        self.cost = cost
        self.prev = prev
        self.action = action
    
    def __eq__(self, other):
        if other == None:
            return False
        return self.pos[0] == other.pos[0] and self.pos[1] == other.pos[1] \
        and self.dir[0] == other.dir[0] and self.dir[1] == other.dir[1] \
        and self.key == other.key and equal_ignore_order(self.unlocked_door, other.unlocked_door) \
        and equal_ignore_order(self.opened_door, other.opened_door)

    # a comparison function for sorting
    def __lt__(self, other):
        return self.cost < other.cost

    def MF(self):
        pos_temp = [self.pos[0] + self.dir[0], self.pos[1] + self.dir[1]]
        return state(pos_temp, self.dir, self.key, self.unlocked_door,self.opened_door, self.cost+1, self, 0)

    ''''''''''
    up = [0, -1]
    down = [0, 1]
    right = [1, 0]
    left = [-1, 0]
    '''''''''''

    def TL(self):
        if self.dir[0] == 0 and self.dir[1] == -1:
            return state(self.pos, [-1, 0], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 1)
        elif self.dir[0] == 0 and self.dir[1] == 1:
            return state(self.pos, [1, 0], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 1)
        elif self.dir[0] == 1 and self.dir[1] == 0:
            return state(self.pos, [0, -1], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 1)
        elif self.dir[0] == -1 and self.dir[1] == 0:
            return state(self.pos, [0, 1], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 1)

    def TR(self):
        if self.dir[0] == 0 and self.dir[1] == -1:
            return state(self.pos, [1, 0], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 2)
        elif self.dir[0] == 0 and self.dir[1] == 1:
            return state(self.pos, [-1, 0], self.key, self.unlocked_door, self.opened_door, self.cost+1, self, 2)
        elif self.dir[0] == 1 and self.dir[1] == 0:
            return state(self.pos, [0, 1], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 2)
        elif self.dir[0] == -1 and self.dir[1] == 0:
            return state(self.pos, [0, -1], self.key, self.unlocked_door, self.opened_door,self.cost+1, self, 2)
        
    def PK(self):
        return state(self.pos, self.dir, True, self.unlocked_door, self.opened_door,self.cost+1, self, 3)

    def UD(self):
        new_opened_door = self.opened_door.copy()
        new_unlocked_door = self.unlocked_door.copy()
        door_pos = [self.pos[0] + self.dir[0], self.pos[1] + self.dir[1]]
        new_opened_door.append(door_pos)
        if door_pos not in self.unlocked_door:
            new_unlocked_door.append(door_pos)
            
        return state(self.pos, self.dir, self.key, unlocked_door=new_unlocked_door, opened_door=new_opened_door, cost=self.cost+1, prev=self, action=4)
    

def dp(env):
    """
    Dynamic Programming
    """

    # The environment may contain a door which blocks the way to the goal. 
    # If the door is closed, the agent needs to pick up a key to unlock the door. 
    # The agent has three regular actions, move forward (MF), turn left (TL), and turn right (TR), and two special actions, pick up key (PK) and unlock door (UD). 
    # Taking any of these five actions costs energy (positive cost). 

    env, info = load_env(env)
    height = info["height"]
    width = info["width"]
    init_agent_pos = info["init_agent_pos"]
    init_agent_dir = info["init_agent_dir"]
    key_pos = info["key_pos"]
    goal_pos = info["goal_pos"]

    print("key_pos: ", key_pos)
    print("goal position: ", goal_pos)

    # Determine whether agent is carrying a key
    is_carrying = env.carrying is not None

    print("is_carrying ", is_carrying)


    # get door information
    unlocked_door = []
    opened_door = []
    for x in range(width):
        for y in range(height):
            cell = env.grid.get(x, y)
            if cell is not None and isinstance(cell, minigrid.core.world_object.Door):
                if cell.is_open:
                    opened_door.append([x, y])
                if not cell.is_locked:
                    unlocked_door.append([x, y])
    
    print("unlocked_door: ", unlocked_door)
    print("opened_door: ", opened_door)


    start = state([init_agent_pos[0], init_agent_pos[1]], init_agent_dir, unlocked_door=unlocked_door, opened_door=opened_door,key=is_carrying, cost=0)

    pq = []
    heapq.heappush(pq, start)
    visited = []
    visited.append(start)

  

    while len(pq) > 0:
        # get the state with the smallest cost
        current = heapq.heappop(pq)
        print("current state: ", current.pos, current.dir,  current.key, current.opened_door, current.cost, current.prev, current.action)

        # if the current state is the goal state, return the cost
        if current.pos[0] == goal_pos[0] and current.pos[1] == goal_pos[1]\
        and current.cost != math.inf:
            # trace back the path
            cost = current.cost
            print("cost: ", cost)
            path = []
            while current.prev != None:
                path.append(current)
                current = current.prev
            return cost, path

        # if the current state is not the goal state, add all possible next states to the queue
        if current.pos[0] != goal_pos[0] or current.pos[1] != goal_pos[1]:

            # turn left
            next = current.TL()
            push_next_to_pq(next, visited, pq)

            # turn right
            next = current.TR()
            push_next_to_pq(next, visited, pq)

            # pick up key
            x = current.pos[0] + current.dir[0]
            y = current.pos[1] + current.dir[1]
            if not (x >= 0 and x < width and y >= 0 and y < height):
                continue
            cell = env.grid.get(x,y)
            if current.key == False \
            and isinstance(cell, minigrid.core.world_object.Key):
                next = current.PK()
                push_next_to_pq(next, visited, pq)

            # unlock door    
            cell = env.grid.get(x,y)
            if isinstance(cell, minigrid.core.world_object.Door):
                if (current.key == True and (not coor_in_list([x,y], current.opened_door))) \
                or (coor_in_list([x,y], current.unlocked_door) and (not coor_in_list([x,y], current.opened_door))):
                    next = current.UD()
                    push_next_to_pq(next, visited, pq)

            # move forward
            next = current.MF()
            if next.pos[0] >= 0 and next.pos[0] < width and next.pos[1] >= 0 and next.pos[1] < height:
                cell = env.grid.get(next.pos[0], next.pos[1])
                if cell is None or (not isinstance(cell, minigrid.core.world_object.Wall)):

                    if not (isinstance(cell, minigrid.core.world_object.Door) \
                    and ([next.pos[0], next.pos[1]] not in current.opened_door)):

                        push_next_to_pq(next, visited, pq)

                   

    return math.inf, []



if __name__ == "__main__":

    known_envs = []
    known_envs.append("envs/known_envs/doorkey-5x5-normal.env")
    known_envs.append("envs/known_envs/doorkey-6x6-normal.env")
    known_envs.append("envs/known_envs/doorkey-8x8-normal.env")

    known_envs.append("envs/known_envs/doorkey-6x6-direct.env")
    known_envs.append("envs/known_envs/doorkey-8x8-direct.env")
    known_envs.append("envs/known_envs/doorkey-6x6-shortcut.env")
    known_envs.append("envs/known_envs/doorkey-8x8-shortcut.env")


    for env_path in known_envs:
        env, info = load_env(env_path)
        cost, path = dp(env_path)

        actions = []
        # positions = []
        # keys = []
        # directions = []
        for i in range(len(path)):
            actions.insert(0,path[i].action)
            # positions.insert(0,path[i].pos)
            # keys.insert(0,path[i].key)
            # directions.insert(0,path[i].dir)

        print(actions)
        # print(positions)
        # print(keys)
        # print(directions)
        draw_gif_from_seq(actions, env, 'gif/' + env_path.split('/')[-1].split('.')[0] + '.gif')

    # draw the gif for envs/random_envs/doorkey-8x8-1.env to envs/random_envs/doorkey-8x8-36.env
    for i in range(1, 37):
        env_path = 'envs/random_envs/doorkey-8x8-' + str(i) + '.env'
        env, info = load_env(env_path)
        cost, path = dp(env_path)
        actions = []
        for i in range(len(path)):
            actions.insert(0,path[i].action)
        draw_gif_from_seq(actions, env, 'gif/' + env_path.split('/')[-1].split('.')[0] + '.gif')

    

        



    
