import pandas as pd
import numpy as np
import math
from datetime import datetime
import matplotlib.pyplot as plt
import random
import time
import os

# Parameters
num_uavs_team = 3
num_vertices = 40
UAV_speed = 5                          # m/s
Flight_time = 20                        # Maximum flight time in minutes
major_ax = UAV_speed * 60 * Flight_time # Major axis calculation based on UAV speed and a factor
charging_station = np.array([50, 100], dtype=float)
magma_colors = plt.get_cmap('magma')(np.linspace(0, 1, num_vertices))

x_data = np.random.choice(101, size=num_vertices, replace = False)  # Random x coordinates between 0 and 100
y_data = np.random.choice(101, size=num_vertices, replace = False)  # Random y coordinates between 0 and 100
x_data[0] = 50
y_data[0] = 100

# Select random start and end points
start_point = 0
end_point = 0

s_point = (x_data[start_point], y_data[start_point])
e_point = (x_data[end_point], y_data[end_point])

input_data = []
for i in range(num_vertices):
    point = (x_data[i], y_data[i])
    # Check if the point is the start or end point and within the allowable distance in one go
    if point != s_point and point != e_point and \
       math.sqrt((s_point[0] - point[0])**2 + (s_point[1] - point[1])**2) + \
       math.sqrt((e_point[0] - point[0])**2 + (e_point[1] - point[1])**2) <= major_ax:
        input_data.append(point)

# input_data = list(set(input_data)) # 리스트 중복제거
inputtuple = list(map(tuple,(input_data)))
# if s_point in input_data:
#     input_data.remove(s_point)
# if e_point in input_data:
#     input_data.remove(e_point)
inputcorr = inputtuple[:] 

nbofnodes = []
distconsmp = []
global route_set
route_set = []
teamscore = 0 # the number of rtop nodes
p = 5 # (%)
iproute = route_set[:]
K = 10
I = 100

def two_opt(tour, dist_matrix):
    n = len(tour)
    improve = True
    while improve:
        improve = False
        for i in range(1, n - 1):
            for j in range(i + 2, n):  # Adjusted to skip unnecessary check when j-i == 1
                new_tour = tour[:]
                new_tour[i:j] = reversed(tour[i:j])  # More pythonic reversal
                new_dist = sum(dist_matrix[new_tour[k]][new_tour[k+1]] for k in range(n-1)) + dist_matrix[new_tour[-1]][new_tour[0]]
                current_dist = sum(dist_matrix[tour[k]][tour[k+1]] for k in range(n-1)) + dist_matrix[tour[-1]][tour[0]]
                if new_dist < current_dist:
                    tour = new_tour
                    improve = True
                    break
            if improve:
                break
    return tour

def distance_matrix(path_set):
    path_array = np.array(path_set)
    dist_matrix = np.linalg.norm(path_array[:, np.newaxis, :] - path_array[np.newaxis, :, :], axis=2)
    return dist_matrix

def tourlength(path_set):
    n = len(path_set)
    inittour = list(range(n))
    
    return inittour

def insertion_main(input_data):
    path_list = [s_point, e_point]  # Start with the initial route from start to end point.
    best_tour_length = float('inf')  # Initialize with infinite tour length for comparison.
    best_route = []

    while input_data:
        add_point = random.choice(input_data)
        input_data.remove(add_point)
        best_update_found = False

        # Attempt to insert the point at every possible position in the path.
        for i in range(1, len(path_list)):
            new_path = path_list[:i] + [add_point] + path_list[i:]
            dist_matrix = distance_matrix(new_path)
            tour = tourlength(new_path)
            tour = two_opt(tour, dist_matrix)
            new_tour_length = sum(dist_matrix[tour[k]][tour[k+1]] for k in range(len(tour) - 1))

            # Update if a shorter tour is found.
            if new_tour_length < best_tour_length:
                best_tour_length = new_tour_length
                best_route = [new_path[j] for j in tour]
                best_update_found = True

        # If no improvement is possible, restore the previous best state and break.
        if not best_update_found or best_tour_length >= major_ax:
            break

    # Collect results for the final route.
    route_set.append(best_route)
    distconsmp.append(best_tour_length)
    nbofnodes.append(len(best_route) - 2)

    return input_data, route_set, distconsmp, nbofnodes


def visited_nodes_list(route_set):
    nodesnumber = []
    for i in range(0, len(route_set)):
        nodesnumber.append(len(route_set[i])-2)

    return nodesnumber

def distance(city1, city2):
    return np.linalg.norm(np.array(city1) - np.array(city2))

def route_distance(cities):
    return sum(distance(cities[i], cities[i+1]) for i in range(len(cities) - 1))

def dist_list(route_set):
    total_dist = []
    for i in range(0, len(route_set)):
        total_dist.append(route_distance(route_set[i])) 
    return total_dist

def finding_top(route_set):
    givenlist = visited_nodes_list(route_set)
    # print(givenlist)
    findmax = givenlist[:]
    findmax = np.array(findmax)

    #FirstMax
    firstMax = max(findmax)

    duplimax = np.where(givenlist == firstMax) # set of index
    duplimax = list(duplimax)

    if len(duplimax[0]) > 1:
        min_dist = distconsmp[duplimax[0][0]]
        for e in range(0,len(duplimax[0])):
            if min_dist > distconsmp[duplimax[0][e]]:
                min_dist = distconsmp[duplimax[0][e]]

    print("firstmax: ", firstMax)
    findmax = np.delete(findmax, np.where(findmax == firstMax))

    #secondMax
    secondMax = max(findmax)

    dupl_max = np.where(givenlist == secondMax) # set of index
    dupl_max = list(dupl_max)

    if len(dupl_max[0]) > 1:
        min_dist = distconsmp[dupl_max[0][0]]
        for e in range(0,len(dupl_max[0])):
            if min_dist > distconsmp[dupl_max[0][e]]:
                min_dist = distconsmp[dupl_max[0][e]]

    print("secmax: ", secondMax)
    findmax = np.delete(findmax, np.where(findmax == secondMax))

    #thirdMax
    thirdMax = max(findmax)

    dupl_max = np.where(givenlist == thirdMax) # set of index
    dupl_max = list(dupl_max)

    if len(dupl_max[0]) > 1:
        min_dist = distconsmp[dupl_max[0][0]]
        for e in range(0,len(dupl_max[0])):
            if min_dist > distconsmp[dupl_max[0][e]]:
                min_dist = distconsmp[dupl_max[0][e]]
    
    print("thirdmax: ", thirdMax)

    zeros_rtop = np.zeros(len(givenlist))
    zeros_rtop[givenlist.index(firstMax)] = 1
    zeros_rtop[givenlist.index(secondMax)] = 1

    record = firstMax + secondMax + thirdMax # rtop의 방문노드 수
    return zeros_rtop, record



# def finding_top(route_set):
#     # Retrieve a list of the number of nodes visited per route
#     givenlist = visited_nodes_list(route_set)
#     findmax = np.array(givenlist)  # Convert list to NumPy array for better performance

#     # Identify the indices of the top num_uavs_team routes with the most visited nodes
#     print("route_set: ", route_set)
#     top_indices = np.argpartition(findmax, -num_uavs_team)[-num_uavs_team:]
#     top_indices = top_indices[np.argsort(-findmax[top_indices])]  # Sort indices by the number of visited nodes in descending order

#     # Calculate the minimum travel distance for routes with the same maximum number of visited nodes
#     top_routes = []
#     for index in top_indices:
#         if len(np.where(givenlist == findmax[index])[0]) > 1:
#             # Find the minimum distance among routes with the same maximum number of visits
#             duplicate_indices = np.where(givenlist == findmax[index])[0]
#             min_dist = distconsmp[duplicate_indices[0]]
#             selected_index = duplicate_indices[0]
#             for dup_index in duplicate_indices:
#                 if distconsmp[dup_index] < min_dist:
#                     min_dist = distconsmp[dup_index]
#                     selected_index = dup_index
#             top_routes.append(selected_index)
#         else:
#             top_routes.append(index)

#     # Create an array indicating the selected top routes
#     zeros_rtop = np.zeros(len(givenlist), dtype=int)
#     for i in top_routes:
#         zeros_rtop[i] = 1

#     # Calculate the total number of visited nodes for the selected top routes
#     record = sum(findmax[top_routes])
#     return zeros_rtop, record

def discrimTOP(rtop, route_set): # 여기서 top_route랑 ntop_route랑 나뉘어짐
    top_route = []
    ntop_route = []

    for e in range(0, len(rtop)):
        if rtop[e] == 1:
            top_route.append(route_set[e])
        else:
            ntop_route.append(route_set[e])

    return top_route, ntop_route

def just_top_routes(routes):
    zero_rtop, record = finding_top(routes)
    top_routes = []

    for e in range(0, len(zero_rtop)):
        if zero_rtop[e] == 1:
            top_routes.append(routes[e])

    return top_routes, record

def step_one_main(routetyple):

    new_list, route_set, distconsmp, nbofnodes = insertion_main(routetyple)

    i=1
    while len(new_list) > 0:
      # print("\nThe {}st iteration".format(i))
      i = i+1
      new_list, route_set, distconsmp, nbofnodes = insertion_main(new_list)

    # print("route_set", route_set)

    # rtop, record = finding_top(route_set)

    # data = {'Number of nodes': nbofnodes, # 방문 노드 수
    #     'Dist-consumption(m)': distconsmp,# 소요 거리 (소요 시간=소요거리 /15)
    #     'R_top': rtop, # RTOP여부 
    #     'Route': route_set}    
        
    # top_route, ntop_route = discrimTOP(rtop, route_set)

    # df = pd.DataFrame(data)
    # df.to_csv(r'/home/jackielee/fastAGC/metahard/csv_results/first_end_sample.csv')
    # route_info = df.values.tolist()
    # deviation = record * p / 100
    return route_set

def inc_teamscore(A_list, B_list): # if teamscore increases, return True
    # 만약 B_list의 dist가 Tmax 보다 같거나 작으면 바로 return False
    if route_distance(B_list) >= major_ax:
        # print("Modified route exceeds the time limit.", route_distance(B_list))
        return False
    
    else:
        if len(A_list) < len(B_list):
            # print("Adist={}'s nodes < Bdist={}'s nodes. Update".format(route_distance(A_list),route_distance(B_list)))
            return True
        elif len(A_list) == len(B_list):
            # A_list와 B_list의 거리 구하기
            A_dist = route_distance(A_list)
            B_dist = route_distance(B_list)
            # print("Adist={}'s dist < Bdist={}'s dist".format(A_dist,B_dist))
            if A_dist > B_dist:
                return True
        else:
            # print("Adist={} is better than Bdist={}".format(A_dist,B_dist))
            return False
        
# def orderofpoint(point, secondorder_list):
#     # point가 2차원 배열에 어느 점에 있는지 위치 리턴
#     for k in range(0,len(secondorder_list)):
#         for kk in range(0,len(secondorder_list[k])):
#             if point == secondorder_list[k][kk]:
#                 return k, kk # 이차원 배열의 [k][kk] 에 있음
            
def orderofpoint(point, routes):
    for route_index, route in enumerate(routes):
        if point in route:
            return route_index, route.index(point)
    return -1, -1  # 포인트를 찾지 못했을 경우의 기본값

def twopointexchange(iproute):
    # print("Run two-point exchange\n")
    zerortop, record = finding_top(iproute)
    rtop_list = []
    rntop_list = []

    for e in range(0, len(zerortop)):
        if zerortop[e] == 1:
            rtop_list.append(iproute[e])
        else:
            rntop_list.append(iproute[e])

    temp = []
    temp_list = []

    for j in range(0,len(rtop_list)):
        for jj in range(1,len(rtop_list[j])-1):
            
            flag = True

            for i in range(0,len(rntop_list)):
                for ii in range(1,len(rntop_list[i])-1):

                    temp_list = rtop_list[j][:] # temp_list는 교환 후 리스트 임시저장소
                    temp_list[jj] = rntop_list[i][ii]

                    if inc_teamscore(rtop_list[j], temp_list) == True:
                        # print("Exchange: rtop_list{} in rtop_route{} with rntop_list{} in rntop_route {}".format(rtop_list[j][jj],j, rntop_list[i][ii],i))

                        # exchange process
                        temp = rntop_list[i][ii]
                        rntop_list[i][ii] = rtop_list[j][jj]
                        rtop_list[j][jj] = temp
                        temp_list.clear()

                        flag = False
                        break

                    else:
                        temp_list.clear()

                    # 여기에 Set best_exchange = feasible_exchange with the highest team score
                    if flag == False:
                        break
                if flag == False :
                    break
            if flag == False:
                break
                    
            # if team score of the best_exchange >= record - deviation:
            #   make the best_exchange
    integratedlist =  rtop_list + rntop_list
    return integratedlist # rtop랑 rntop가 합쳐진 형태

def onepointmovement(inputcorr, iproute):
    for i in range(len(inputcorr)):
        point = inputcorr[i]
        k, kk = orderofpoint(point, iproute)

        if k == -1:  # 유효하지 않은 인덱스 처리
            continue  # 이 포인트를 건너뛰고 다음 포인트로 넘어감

        for j in range(len(iproute)):
            if j == k:  # 같은 경로에 있으면 스킵
                continue

            for jj in range(1, len(iproute[j]) - 1):
                temp_list = iproute[j][:]  # 현재 경로 복사
                temp_list.insert(jj, point)  # 포인트 삽입 시도

                if inc_teamscore(iproute[j], temp_list):
                    # 점수가 개선되면 업데이트
                    iproute[k].remove(point)  # 기존 위치에서 삭제
                    iproute[j].insert(jj, point)  # 새 위치에 삽입
                    break
            else:
                continue
            break

    return iproute

# def onepointmovement(inputcorr, iproute):
#     temp_list = []
#     for i in range(0, len(inputcorr)):
#         point = inputcorr[i]
#         flag = True
#         k, kk = orderofpoint(inputcorr[i], iproute)

#         if k == -1:  # 유효하지 않은 인덱스 처리
#             continue  # 이 포인트를 건너뛰고 다음 포인트로 넘어감

#         for j in range(0,len(iproute)): 
#             # 그전에 i랑 j가 같은 path에 있는거면 안됨.
#             # print("inputcorr", inputcorr)
#             # print("inputcorr[i]", inputcorr[i])
#             # print("iproute", iproute)
#             # k, kk = orderofpoint(inputcorr[i], iproute)

#             if k == j :
#                 # print("I am in the route {} with the point {}. We are in the same route. j++ and try again".format(j, inputcorr[i]))
#                 # flag = True
#                 continue

#             else:
#                 # print("I am in the route {}.".format(j))
#                 for jj in range(1,len(iproute[j])-1): #시작점 끝점 빼고
#                     temp_list = iproute[j][:]
#                     temp_list.insert(jj, inputcorr[i])

#                     if inc_teamscore(iproute[j], temp_list) == True: # teamscore increased
                        
#                         # print("\n점 {}를 넣을지말지 돌려보자!".format(inputcorr[i]))
#                         # 기존 점 제거
#                         del iproute[k][kk]

#                         # jj앞에 점 추가
#                         # print("route {}의 {}앞에 {}를 추가할게요~".format(j, iproute[j][jj], inputcorr[i]))
#                         flag = False
#                         iproute[j].insert(jj, inputcorr[i])
#                         temp_list.clear()
#                         break

#                     else: # teamscore didn't increase. or it exceeds time constraint
#                         temp_list.clear()
                        

#                     # 여기에 Set best_movement = feasible_movement with the highest team score
#                     if flag == False:
#                         break
#                 if flag==False:
#                     break
            
 
#         # if teamscore of the best_movement >= record - deviation,
#         #   make the best_movement
    
#     return iproute

def two_opt_cu(asetofroute): # tour is like index of nodes
    dist_matrix = distance_matrix(asetofroute)
    tour = tourlength(asetofroute)
  
    n = len(tour)
    improve = True
    while improve:
      improve = False
      for i in range(1, n-1):
          for j in range(i+1, n):
            if j-i == 1:
                continue
            new_tour = tour[:]
            new_tour[i:j] = tour[j-1:i-1:-1] #reverse process
            new_dist = np.sum([dist_matrix[new_tour[k]][new_tour[k+1]] for k in range(n-1)]) + dist_matrix[new_tour[n-1]][new_tour[0]]
            if new_dist < np.sum([dist_matrix[tour[k]][tour[k+1]] for k in range(n-1)]) + dist_matrix[tour[n-1]][tour[0]]:
                tour = new_tour
                improve = True
                break
          if improve:
              break

    modiroute = [0 for i in range(len(asetofroute))]
    for k in range(0, len(asetofroute)):
        modiroute[k] = asetofroute[tour[k]]

    return modiroute

def cleanup(route_sets):
    cleanupset = []
    for i in range(0,len(route_sets)):
        cleanupset.append(two_opt_cu(route_sets[i]))

    return cleanupset

def cheapest_insertion(node, nroutes): # nroutes 에 node를 cheapsest way로 추가
    rntopsets = nroutes[:]
    first, second = 0,0
    for i in range(0, len(rntopsets)):
        for j in range(1, len(rntopsets[i])-1):
            delta_dist = 0
            if i ==0 and j == 1:
                before_dist = route_distance(rntopsets[i])
                rntopsets[i].insert(j, node) #넣고 
                after_dist = route_distance(rntopsets[i])
                delta_dist = after_dist - before_dist #값비교하고
                first, second = i, j # 값 저장하고
                del rntopsets[i][j] #빼고
                # print("delta_dist:", delta_dist)
                # print(first,second)

            else:
                before_dist = route_distance(rntopsets[i])
                rntopsets[i].insert(j, node) #넣고 
                after_dist = route_distance(rntopsets[i])
                
                if delta_dist > after_dist - before_dist:
                    delta_dist = after_dist - before_dist
                    first,second = i, j
                    del rntopsets[i][j] #빼고
                else:
                    del rntopsets[i][j] #빼고
                # print("delta_dist:", delta_dist)
                # print(first,second)
        
    nroutes[first].insert(second,node)
    # print(nroutes)
    return nroutes

# for K in range(1,11):
def reinit_one(routes, K): # remove k point from RTOP # p = 5
    print("\nReinit_one now!")
    # a는 rtop에 있는 점들
    rtop, record = finding_top(routes)
    top_route = []
    ntop_route = []

    for e in range(0, len(rtop)):
        if rtop[e] == 1:
            top_route.append(route_set[e])
        else:
            ntop_route.append(route_set[e])
    

    # topintegration에 s, e 빼고 integration 점들 다 집어넣기
    topintegration = []
    for h in range(0,len(top_route)):
        for hh in range(1, len(top_route[h])-1):
            topintegration.append(top_route[h][hh])

    for i in range(0,len(topintegration)):
        term = distance(s_point, topintegration[i]) + distance(e_point,topintegration[i])
        if term <= major_ax - ((K-1)*major_ax/10) and term > major_ax - (K*major_ax/10): # 1 = K
            # top가 0과 1 만 있을 때, topinegration[i]를 제거 하고 
            if topintegration[i] in top_route[0]:
                top_route[0].remove(topintegration[i])
            else :
                top_route[1].remove(topintegration[i])
            # rtop에 있는 루트중에 하나에 cheapest insertion.
            ntop_route = cheapest_insertion(topintegration[i], ntop_route)       
    
    newroutes = top_route + ntop_route
    # print("newroutes", newroutes)
    return newroutes    
    
def reinit_two(routes, K): # remove k point from RTOP # p = 2.5
    print("\nReinit_two now!")
    # a는 rtop에 있는 점들
    rtop, record = finding_top(routes)
    top_route = []
    ntop_route = []

    for e in range(0, len(rtop)):
        if rtop[e] == 1:
            top_route.append(route_set[e])
        else:
            ntop_route.append(route_set[e])

    # topintegration에 s, e 빼고 integration 점들 다 집어넣기
    topintegration = []
    for h in range(0,len(top_route)):
        for hh in range(1, len(top_route[h])-1):
            topintegration.append(top_route[h][hh])

    for i in range(0,len(topintegration)):
        term = distance(s_point, topintegration[i]) + distance(e_point,topintegration[i])
        if term <= major_ax - ((K-1)*major_ax/10) and term > major_ax - (K*major_ax/10): # 1 = K
            # top가 0과 1 만 있을 때, topinegration[i]를 제거 하고 
            if topintegration[i] in top_route[0]:
                top_route[0].remove(topintegration[i])
            else :
                top_route[1].remove(topintegration[i])
            # rtop에 있는 루트중에 하나에 cheapest insertion.
            ntop_route = cheapest_insertion(topintegration[i], ntop_route)       
    
    newroutes = top_route + ntop_route
    # print("newroutes", newroutes)
    return newroutes  

def makethemcsv(listtocsv):
    top, record = finding_top(listtocsv)
    data = {
        'Number of nodes': visited_nodes_list(listtocsv),
        'Dist-consumption(m)': dist_list(listtocsv),
        'R_top': top, 
        'Route': listtocsv
    }
    df = pd.DataFrame(data)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    # Save in the current directory or specify a relative path
    save_path = os.path.join('.', 'csv_results')  # Saves in a folder named 'csv_results' in the current directory
    if not os.path.exists(save_path):
        os.makedirs(save_path)  # Creates the directory if it does not exist
    df.to_csv(os.path.join(save_path, filename))


def remove_zeroset(result_list): ## nb of nodes가 0 이면 그 루트 아예 제거
    tided_list = []
    for i in range(0,len(result_list)):
        if len(result_list[i]) == 2:
            tided_list.append(i)

    for j in range(0, len(tided_list)):
        tided_list.sort(reverse=True)
        del result_list[tided_list[j]]
        
    return result_list

def improvement(inputcorr, route_set): 
    rout_set = twopointexchange(route_set)
    rout_set = onepointmovement(inputcorr, rout_set) # inputcorr is the global variable.
    rout_set = cleanup(rout_set)
    rout_set = remove_zeroset(rout_set) # 0 visited routed removal

    # makethemcsv(rout_set)

    return rout_set

def update_route(prev_routes, curr_routes, curr_i_record):
    prev_routes[:] = curr_routes
    return curr_i_record

def process_improvements(prev_routes, curr_routes, prev_rtop, curr_rtop, prev_i_record, curr_i_record):
    """ 개선 처리를 위한 별도 함수 """
    if prev_routes != curr_routes:
        dist_curr_rtop = route_distance(curr_rtop[0]) + route_distance(curr_rtop[1])
        dist_prev_rtop = route_distance(prev_rtop[0]) + route_distance(prev_rtop[1])
        if curr_i_record > prev_i_record or (curr_i_record == prev_i_record and dist_curr_rtop < dist_prev_rtop):
            update_route(prev_routes, curr_routes, curr_i_record)
            return True
    return False

def step_two_main(route_set, K=10, I=100):
    """ 메인 루프 실행 함수 """
    routes = route_set[:]
    for k in range(1, K):
        for i in range(1, I):
            if i == 1:
                routes = improvement(inputcorr, routes)
                prev_routes, prev_rtop, prev_i_record = routes[:], *just_top_routes(routes)
            else:
                routes = improvement(inputcorr, routes)
                curr_rtop, curr_i_record = just_top_routes(routes)
                if not process_improvements(prev_routes, routes, prev_rtop, curr_rtop, prev_i_record, curr_i_record):
                    break
            if i >= 5:  # 5번 반복 후 개선이 없으면 중단
                print("No improvement in 5 iterations.")
                break
        reinit_one(routes, k)
    print("Final result: {}, record: {}".format(prev_routes, prev_i_record))
    return prev_routes

# def step_two_main(route_set):
#     routes = route_set[:]

#     for k in range(1, K):
#         flag = True
#         for i in range(1,I):
#             counting_record = 0
#             improve = True

#             if k == 1 and i == 1 : # 한번만 실행
#                 # print("\nFirst improvement!")
#                 routes = improvement(inputcorr, routes)

#                 prev_routes = routes[:]
#                 prev_rtop, prev_i_record = just_top_routes(routes)
            
#             else:
#                 # print("\nNext improvement!")
#                 routes = improvement(inputcorr, routes)

#                 curr_rtop, curr_i_record = just_top_routes(routes)
#                 curr_routes = routes[:]

#                 if prev_routes != curr_routes: # 루트의 변화가 존재
#                     if curr_i_record == prev_i_record: #record는 같지만 값이 달라졌는지
#                         # print("record는 같은데 movement 변화만 있음")
#                         dist_curr_rtop = route_distance(curr_rtop[0]) + route_distance(curr_rtop[1])
#                         dist_prev_rtop = route_distance(prev_rtop[0]) + route_distance(prev_rtop[1])
#                         if dist_curr_rtop < dist_prev_rtop: #방문노드수는 같은데 거리가 줄어듦 (개선됨)
#                             counting_record = 0
#                             prev_i_record = curr_i_record
#                             prev_rtop = curr_rtop
#                             prev_routes = curr_routes[:]

#                             record = curr_i_record
#                             deviation = record * p /100
                            

#                         else: #record는 같은데 값은 더 안좋아짐 (개선안됨)
#                             # print("record는 같은데 개선되지는 않았다. prev가 더 좋음")
#                             counting_record = counting_record + 1
                            

#                     elif curr_i_record > prev_i_record: # record가 더 나아짐. curr_i_record > prev_i_record (개선됨)
#                         counting_record = 0
#                         print("Got better record. present record:{}. previous record:{}".format(curr_i_record, prev_i_record))
#                         prev_i_record = curr_i_record
#                         prev_rtop = curr_rtop
#                         prev_routes = curr_routes[:]

#                         record = curr_i_record
#                         deviation = record * p /100
                    
#                     else: # 변화가 있기는 한데 개선되지는 않았음. curr_i_record < prev_i_record (개선안됨)
#                         # print("변화가 있기는 있지만 개선되지는 않았다. prev가 더 좋음")
#                         counting_record = counting_record + 1
#                         pass
                

#                 else: # prev_i랑 curr_i 가 같아서 더이상 변화자체가 없음
#                     improve = False
#                     counting_record = counting_record + 1
#                     break

#             if improve == False:
#                 break

#             if counting_record == 5:
#                 print("no new record in 5 iterations. Break")
#                 flag = False
#                 break
        
#         if flag == False:
#             break
#         reinit_one(routes, k)

#     print("Final result:{},record:{}".format(prev_routes, prev_i_record))
#     return prev_routes

# def step_three_main(route_set):
#     p = 2.5
#     routes = route_set[:]
#     for k in range(1,K):
#         flag = True
#         for i in range(1,I):
#             counting_record = 0
#             improve = True

#             if k == 1 and i == 1 : # 한번만 실행
#                 # print("\nFirst improvement!")
#                 routes = improvement(inputcorr, routes)

#                 prev_routes = routes[:]
#                 prev_rtop, prev_i_record = just_top_routes(routes)
            
#             else:
#                 # print("\nNext improvement!")
#                 routes = improvement(inputcorr, routes)

#                 curr_rtop, curr_i_record = just_top_routes(routes)
#                 curr_routes = routes[:]

#                 if prev_routes != curr_routes: # 루트의 변화가 존재
#                     if curr_i_record == prev_i_record: #record는 같지만 값이 달라졌는지
#                         # print("record는 같은데 movement 변화만 있음")
#                         dist_curr_rtop = route_distance(curr_rtop[0]) + route_distance(curr_rtop[1])
#                         dist_prev_rtop = route_distance(prev_rtop[0]) + route_distance(prev_rtop[1])
#                         if dist_curr_rtop < dist_prev_rtop: #방문노드수는 같은데 거리가 줄어듦 (개선됨)
                            
#                             prev_i_record = curr_i_record
#                             prev_rtop = curr_rtop
#                             prev_routes = curr_routes[:]

#                             record = curr_i_record
#                             deviation = record * p /100
                            

#                         else: #record는 같은데 값은 더 안좋아짐 (개선안됨)
#                             # print("record는 같은데 개선되지는 않았다. prev가 더 좋음")
#                             counting_record = counting_record + 1
                            

#                     elif curr_i_record > prev_i_record: # record가 더 나아짐. curr_i_record > prev_i_record (개선됨)
#                         counting_record = 0
#                         print("Got better record. present record:{}. previous record:{}".format(curr_i_record, prev_i_record))
#                         prev_i_record = curr_i_record
#                         prev_rtop = curr_rtop
#                         prev_routes = curr_routes[:]

#                         record = curr_i_record
#                         deviation = record * p /100
                    
#                     else: # 변화가 있기는 한데 개선되지는 않았음. curr_i_record < prev_i_record (개선안됨)
#                         # print("변화가 있기는 있지만 개선되지는 않았다. prev가 더 좋음")
#                         counting_record = counting_record + 1
#                         pass
                

#                 else: # prev_i랑 curr_i 가 같아서 더이상 변화자체가 없음
#                     improve = False
#                     counting_record = counting_record + 1
#                     break

#             if improve == False:
#                 break

#             if counting_record == 5:
#                 print("no new record in 5 iterations. Break")
#                 flag = False
#                 break
        
#         if flag == False:
#             break
#         reinit_two(routes, k)

#     print("Final result:{},record:{}".format(prev_routes, prev_i_record))
#     return prev_routes

def step_three_main(route_set, K=10, I=100, p=2.5):
    routes = route_set[:]
    for k in range(1, K):
        for i in range(1, I):
            if i == 1:  # 처음 실행 시 초기 개선
                routes = improvement(inputcorr, routes)
                prev_routes, prev_rtop, prev_i_record = routes[:], *just_top_routes(routes)
            else:
                routes = improvement(inputcorr, routes)
                curr_rtop, curr_i_record = just_top_routes(routes)
                curr_routes = routes[:]
                if not process_route_changes(prev_routes, curr_routes, prev_rtop, curr_rtop, prev_i_record, curr_i_record, p):
                    break  # 개선이 없으면 반복 중단

            # 지속적인 개선이 없는 경우 중단
            if i >= 5:
                print("No improvement in 5 iterations. Break")
                break

        reinit_two(routes, k)  # 다시 초기화 함수 실행

    print(f"Final result: {prev_routes}, record: {prev_i_record}")
    return prev_routes

def process_route_changes(prev_routes, curr_routes, prev_rtop, curr_rtop, prev_i_record, curr_i_record, p):
    """조건에 따라 경로의 개선 여부를 처리하고 결과를 반환"""
    if prev_routes != curr_routes:
        dist_curr_rtop = route_distance(curr_rtop[0]) + route_distance(curr_rtop[1])
        dist_prev_rtop = route_distance(prev_rtop[0]) + route_distance(prev_rtop[1])
        if curr_i_record > prev_i_record or (curr_i_record == prev_i_record and dist_curr_rtop < dist_prev_rtop):
            prev_routes[:] = curr_routes  # 경로 업데이트
            prev_i_record = curr_i_record
            return True  # 개선이 있었다고 반환
        else:
            return False  # 개선이 없었다고 반환
    return False  # 변화 없으면 False 반환


def basic_map():
    # Basic mapping
    plt.figure(figsize=(7,7))
    plt.grid(True)
    plt.scatter(x_data[1:], y_data[1:], s=30, facecolors='gray', edgecolors='none', alpha = 0.2,  label = 'Verticies')
    plt.scatter(x_data[start_point], y_data[start_point], s= 150, c = 'r',marker='*', label = 'Charging Station')
    
def drawing_top(routes, caption, num_uavs_team):
    basic_map()

    colors = plt.cm.viridis(np.linspace(0, 1, num_uavs_team))  # 색상 배열 생성

    for index, route in enumerate(routes):
        if len(route) < 2:
            continue  # 노드가 1개 또는 0개인 경로는 건너뛰기
        x_coords = [coord[0] for coord in route]
        y_coords = [coord[1] for coord in route]
        
        # 경로와 함께 마커 그리기
        plt.plot(x_coords, y_coords, color=colors[index], marker='o', label=f'UAV {index+1} route visits: {len(route)-2} nodes')

    plt.title(caption)
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.legend()
    plt.show()

# def drawing_top(routes,caption):
#     basic_map()

#     x_alpha = []
#     y_alpha = []

#     firsttop = routes[0]
#     for h in range(0,len(firsttop)):
#         for l in range(1,len(firsttop)):
#             x_alpha.insert(l, firsttop[h][0])
#             y_alpha.insert(l, firsttop[h][1])

#     plt.plot(x_alpha, y_alpha, 'b', marker='^', label = '1st Rtop route visits: {} nodes'.format(len(routes[0])-2))

#     xx_alpha = []
#     yy_alpha = []

#     secondtop = routes[1]
#     for h in range(0,len(secondtop)):
#         for l in range(0,len(secondtop)):
#             xx_alpha.insert(l, secondtop[h][0])
#             yy_alpha.insert(l, secondtop[h][1])

#     plt.plot(xx_alpha, yy_alpha, c = 'g', marker='o', label = '1st Rtop route visits: {} nodes'.format(len(routes[1])-2))

#     plt.title(caption)
#     plt.xlabel('X (m)')
#     plt.ylabel('Y (m)')
#     plt.legend()

#     plt.show()

if __name__ == "__main__":
    start_time = time.time()

    final_routes = step_one_main(inputtuple)
    final_routes = step_two_main(final_routes)
    final_routes = step_three_main(final_routes)
    
    makethemcsv(final_routes)
    print("--- %s seconds ---" % (time.time() - start_time))

    drawing_top(final_routes,"Final routes")

