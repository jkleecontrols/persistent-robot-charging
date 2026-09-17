import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import time

# 시간 측정 시작
start_time = time.time()

# 초기 설정 변경
num_uavs = 4
num_charging_docks = 2
num_vertices = 40  # 노드 수
frame_number = 34  # 프레임 수
uav_speed = 16
battery_drain = 4.5
battery_charge = 6.5
charging_station = np.array([50, 100], dtype=float)  # 중앙 위치
magma_colors = plt.get_cmap('magma')(np.linspace(0, 1, 100))

# vertices 생성 시 검정 박스 영역을 제외하고 생성
vertices = np.array([np.random.rand(2) * 100 for _ in range(num_vertices) if not (45 <= np.random.rand(2)[0] * 100 <= 55 and 45 <= np.random.rand(2)[1] * 100 <= 55)])

# UAV별 방문할 vertices 분배, vertices 개수를 초과하지 않도록 확인

# 배터리 상태 및 위치 초기화
battery_levels = np.full(num_uavs, 100.0)
uav_positions = np.array([charging_station] * num_uavs, dtype=float)  # 모든 UAV는 검정 박스 위치에서 시작
uav_colors = sns.husl_palette(n_colors=num_uavs)  # UAV colors

# 방문된 vertices 추적
visited = np.zeros(num_vertices, dtype=bool)
visit_time = np.full(num_vertices, -1, dtype=int)  # 방문 시간 초기화
color_indices = np.zeros(num_vertices, dtype=int)  # 색상 인덱스 초기화

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 7), gridspec_kw={'width_ratios': [1, 0.5]})
plt.subplots_adjust(top=0.75)

# 사분면별로 점 분류
def classify_quadrants(point):
    x, y = point
    if x > 50 and y > 50:
        return 0  # 1사분면
    elif x < 50 and y > 50:
        return 1  # 2사분면
    elif x < 50 and y < 50:
        return 2  # 3사분면
    elif x > 50 and y < 50:
        return 3  # 4사분면

# 경로의 총 거리를 계산하는 함수
def route_distance(route):
    dist = 0.0
    for i in range(1, len(route)):
        dist += np.linalg.norm(route[i - 1] - route[i])
    return dist

# 2-opt 알고리즘을 적용하는 함수
def apply_2opt(route, improve_threshold=0.01):
    best_route = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 2, len(route)):
                if j - i == 1: continue  # 이웃한 점은 변경 X
                new_route = best_route[:]
                new_route[i:j] = best_route[j-1:i-1:-1]  # 두 점 사이를 뒤집기
                if route_distance(new_route) < route_distance(best_route) - improve_threshold:
                    best_route = new_route
                    improved = True
        route = best_route
    return best_route

# 시작점과 끝점을 (50,100)으로 고정하고 나머지 경로를 최적화
def optimize_path(paths):
    start_end_point = np.array([50, 100])
    optimized_paths = {}
    for key, path in paths.items():
        if path:  # 경로가 비어있지 않은 경우에만 처리
            # 각 경로에 시작점과 끝점 추가
            full_path = np.vstack([start_end_point, np.array(path), start_end_point])
            optimized_path = apply_2opt(full_path)
            optimized_paths[key] = optimized_path
    return optimized_paths

# 각 UAV별 랜덤 경로 설정
paths = {0: [], 1: [], 2: [], 3: []}

for vertex in vertices:
    quadrant = classify_quadrants(vertex)
    paths[quadrant].append(vertex)

# 각 사분면의 점 출력 확인
for quadrant, points in paths.items():
    print(f"Quadrant {quadrant+1} has {len(points)} points.")

paths = optimize_path(paths)

# UAV 초기 위치 설정
uav_positions = np.array([charging_station for _ in range(num_uavs)], dtype=float)
uav_paths = {uav: [uav_positions[uav].copy()] for uav in range(num_uavs)}

# Initialize lines for each UAV
lines = {uav: ax1.plot([], [], color=uav_colors[uav], linewidth=2, label=f'UAV {uav}')[0] for uav in range(num_uavs)}
path_data = {uav: np.array([paths[uav][0]]) for uav in range(num_uavs)}  # Initialize with the first coordinate

# UAV의 현재 목표 위치 인덱스를 저장하는 배열 초기화
current_targets = [0] * num_uavs  # 모든 UAV의 시작 목표 인덱스를 0으로 설정

def interpolate_position(start, end, fraction):
    """Linearly interpolate between start and end points."""
    return (start[0] + (end[0] - start[0]) * fraction, start[1] + (end[1] - start[1]) * fraction)

def init():
    global switches
    switches = []
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, num_uavs)
    ax1.add_patch(plt.Rectangle((45, 95), 10, 10, color='black', label='Charging Station'))  # Station rectangle

    for uav in range(num_uavs):
        lines[uav].set_data(path_data[uav][:, 0], path_data[uav][:, 1])
    ax1.legend()

    # Dynamic text showing the number of UAVs and docks
    global text_handle
    text_handle = fig.text(0.5, 0.95, f"Number of charging docks = {num_charging_docks}, Number of vehicles = {num_uavs}", fontsize=10, ha='center', va='top')
    fig.text(0.5, 0.90, "Status of Charging Docks (Red: on charge)", fontsize=10, ha='center', va='top', transform=fig.transFigure)

    # Position switches at the bottom of the figure
    bottom_y = 0.85  # Normalized coordinate for bottom placement
    text_y = 0.1  # Lower position for text to make room for circles above
    circle_radius = 0.015  # Radius to maintain a round shape

    text_width = 0.5
    spacing = 0.05  # Spacing between circles
    start_x = text_width - (num_charging_docks - 1) * spacing / 2  # Start x based on number of docks to center them

    for i in range(num_charging_docks):
        circle_x = start_x + i * spacing  # Adjust x-position to be centered
        circle = plt.Circle((circle_x, bottom_y), circle_radius, transform=fig.transFigure, edgecolor='black', facecolor='none')
        fig.add_artist(circle)
        switches.append(circle)
    
    return [] #lines.values()

def update(frame):

    # 그래픽 객체만 초기화
    ax1.patches.clear()  # 모든 패치를 제거 (예: UAV 표현)
    for line in lines.values():
        line.set_data([], [])  # 기존 선 데이터 초기화 (이전 프레임의 데이터 제거)

    # ax1.clear()
    ax2.clear()
    ax1.set_title(f"Time: {frame} seconds")
    ax2.set_title("Current Battery Status")
    ax1.add_patch(plt.Rectangle(charging_station - 5, 10, 10, color='black'))

    # Reset limits after clearing
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_xlim(0,100)
    ax1.set_ylim(0,100)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, num_uavs)

    # Vertices 그리기
    for i, pos in enumerate(vertices):
        ax1.scatter(*pos, color='black')

    # 각 UAV 업데이트 및 배터리 상태 그리기
    battery_box_height = 1
    # Define triangle size
    triangle_height = 1  # Height of the triangle
    triangle_width = 5   # Base width of the triangle

    # Redraw dynamic text
    text_handle.set_text(f"Number of charging docks = {num_charging_docks}, Number of vehicles = {num_uavs}")
    
    for i in range(num_uavs):

        # 여기서부터 drone
        if (i < 2 and frame > 20) or (i >= 2 and frame <= 14):
            uav_positions[i] = charging_station
            current_targets[i] = 0  # 충전 중이거나 대기 중일 때는 목표를 재설정
        else:
            # 현재 목표 위치 설정
            target = np.array(paths[i][current_targets[i]], dtype=float)
            direction = target - uav_positions[i]
            distance = np.linalg.norm(direction)

            if distance > uav_speed:
                # 목표까지의 거리가 UAV 속도보다 크면 방향으로 이동
                direction = direction / distance * uav_speed
                uav_positions[i] += direction
            else:
                # 목표에 도달하면 다음 목표로 인덱스를 업데이트
                uav_positions[i] = target  # 목표 위치에 정확히 도달
                if current_targets[i] < len(paths[i]) - 1:
                    current_targets[i] += 1  # 다음 목표로 이동
        
        # 선 데이터 업데이트
        path_data[i] = np.vstack([path_data[i], uav_positions[i]])
        lines[i].set_data(path_data[i][:, 0], path_data[i][:, 1])

        # current_position = uav_positions[i]
        # if frame == 0:
        #     path_data[i] = np.array([current_position])
        # else:
        #     path_data[i] = np.vstack([path_data[i], current_position])
        
        # lines[i].set_data(path_data[i][:, 0], path_data[i][:, 1])  # 선 데이터 업데이트

        # Draw UAVs
        ax1.add_patch(plt.Polygon(uav_positions[i] + np.array([[0, 2], [-1, -1], [1, -1]]),
                                  closed=True, color=uav_colors[i], edgecolor='black', linewidth=2))

        #여기까지 드론
        
        # Update battery levels based on UAV number and frame
        if i < 2:  # UAV1 and UAV2
            if frame <= 20:
                battery_levels[i] -= battery_drain
            else:
                battery_levels[i] += battery_charge
        else:  # UAV3 and UAV4
            if frame > 14:
                battery_levels[i] -= battery_drain

        # Ensuring battery levels stay within 0-100%
        battery_levels[i] = max(10, min(battery_levels[i], 100))

        # Display battery status
        ax2.add_patch(plt.Rectangle((5, i * (battery_box_height + 5)), 50, battery_box_height, edgecolor='black', facecolor='none'))
        battery_fill = (battery_levels[i] / 100.0) * 50
        ax2.add_patch(plt.Rectangle((5, i * (battery_box_height + 5)), battery_fill, battery_box_height, facecolor='green' if battery_levels[i] > 50 else 'red'))

        # Label text with UAV number
        ax2.text(-9, i * (battery_box_height + 5) + battery_box_height / 2, f'UAV {i+1}', verticalalignment='center')

        # Define text for battery percentage
        text_x = 60  # x position for battery percentage text
        text_y = i * (battery_box_height + 5) + battery_box_height / 2
        ax2.text(text_x, text_y, f'{battery_levels[i]:.1f}%', verticalalignment='center')

        # Draw UAV icon to the right of the battery percentage
        icon_x = text_x -1  # x position adjusted to be right of the battery text
        icon_y = text_y

        triangle_points = [(icon_x, icon_y),  # Top point of the triangle
                            (icon_x - triangle_width / 2, icon_y - triangle_height / 2),  # Bottom left point
                            (icon_x - triangle_width / 2, icon_y + triangle_height / 2) ] # Bottom right point    
        ax2.add_patch(plt.Polygon(triangle_points, closed=True, color=uav_colors[i], edgecolor='black', linewidth=1))

    # Update charging dock statuses
    for i, switch in enumerate(switches):
        switch.set_facecolor('red' if (frame <= 14 or frame > 20) and frame <= 34 else 'none')

    ax1.legend(loc='upper right').set_visible(False)
    # 눈금 제거 및 축 범위 설정
    ax2.set_xlim(0, 70)
    ax2.set_ylim(-1, num_uavs * (battery_box_height + 5))
    ax2.axis('off')  # 축과 눈금 제거

    return [lines[i] for i in range(num_uavs)]

# ani = animation.FuncAnimation(fig, update, frames=frame_number, init_func=init, repeat=False)
ani = animation.FuncAnimation(fig, update, frames=frame_number, init_func=init, interval=50, repeat=False)

# 시간 측정 종료 및 출력
end_time = time.time()

plt.show()

print("Total Execution Time: {:.2f} seconds".format(end_time - start_time))
