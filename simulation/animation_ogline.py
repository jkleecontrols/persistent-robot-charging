import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import time
from matplotlib.animation import FFMpegWriter


# 글씨 크기 전역 설정
plt.rc('font', size=12)         # 기본 글씨 크기
plt.rc('axes', titlesize=16)    # 축 제목 크기
plt.rc('axes', labelsize=14)    # 축 라벨 크기
plt.rc('xtick', labelsize=12)   # x축 눈금 글씨 크기
plt.rc('ytick', labelsize=12)   # y축 눈금 글씨 크기
plt.rc('legend', fontsize=12)   # 범례 글씨 크기
plt.rc('figure', titlesize=18)  # 그림 제목 크기

# 시간 측정 시작
start_time = time.time()

# 초기 설정 변경
num_uavs = 3
uav_numbers = [1,2,7]
num_charging_docks = 2
num_vertices = 50  # 노드 수
frame_number = 50  # 프레임 수
global uav_speed
uav_speed = 16*4

# 비행 시퀀스 정의
flight_sequences = {
    0: [[4, 6], [10, 12], [16, 18], [22, 24], [28, 30], [34, 36]],
    1: [[5, 9], [14, 18], [23, 27], [32, 36]],
    2: [[1, 4], [13, 22], [31, 36]],
    3: []
}

p_5m_5to9_32to36 = [[50, 100], [7.4, 39.3], [7.9, 31.6], [1.1, 19.9], [2.8, 30.4], [50, 100]] # 4753.4403
p_4m_1to4 = [[50, 100], [4.2, 59.6], [8.3, 67.6], [13.1, 86.4], [50, 100]] # 3219.7768
p_6m_31to36 = [[50, 100], [33.4, 74.9], [26.4, 72.0], [27.9, 64.7], [24.7, 42.5], [21.6, 38.1], [27.0, 36.4], [17.3, 10.1], [17.7, 5.2], [26.7, 2.0], [33.8, 26.9], [35.4, 29.4], [36.1, 48.6], [44.6, 60.5], [50, 100]] # 5591.5005
p_3m_4to6_28to30 = [[50, 100], [95.1, 71.4], [97.4, 68.9], [50, 100]] # 2837.3196
p_3m_10to12_22to24_34to36 = [[50, 100], [88.7, 97.4], [89.9, 73.4], [84.7, 77.8], [82.1, 81.5], [50, 100]] # 2780.0143
p_10m_13to22 = [[50, 100], [85.4, 69.1], [88.1, 37.3], [90.2, 18.4], [89.7, 12.9], [81.0, 4.5], [74.3, 2.8], [49.7, 14.6], [26.7, 2.0], [17.7, 5.2], [17.3, 10.1], [52.6, 16.7], [64.1, 18.4], [79.6, 18.1], [83.4, 21.7], [73.8, 29.6], [75.6, 52.4], [57.6, 51.2], [52.8, 57.4], [56.8, 62.8], [61.7, 59.6], [61.5, 63.4], [64.5, 63.3], [61.8, 78.4], [57.2, 80.9], [50, 100]] # 9504.0887
p_5m_14to18_23to27 =[[50, 100], [49.1, 86.8], [44.6, 60.5], [35.4, 29.4], [33.8, 26.9], [27.0, 36.4], [21.6, 38.1], [24.7, 42.5], [36.1, 48.6], [27.9, 64.7], [26.4, 72.0], [33.4, 74.9], [50, 100]] # 4353.9823
p_3m_16to18 = [[50, 100], [70.2, 71.9], [72.8, 69.9], [44.6, 60.5], [50, 100]] # 2687.0035

# UAV 0의 경로 생성
path_uav0 = []
path_uav0.extend(p_3m_4to6_28to30)  # 4~6 프레임
path_uav0.extend(p_3m_10to12_22to24_34to36)  # 10~12 프레임
path_uav0.extend(p_3m_16to18)  # 16~18 프레임
path_uav0.extend(p_3m_10to12_22to24_34to36)  # 22~24 프레임
path_uav0.extend(p_3m_4to6_28to30)  # 28~30 프레임
path_uav0.extend(p_3m_10to12_22to24_34to36)  # 34~36 프레임

path_uav1 = []
path_uav1.extend(p_5m_5to9_32to36)
path_uav1.extend(p_5m_14to18_23to27)
path_uav1.extend(p_5m_14to18_23to27)
path_uav1.extend(p_5m_5to9_32to36)

path_uav2 = []
path_uav2.extend(p_4m_1to4)
path_uav2.extend(p_10m_13to22)
path_uav2.extend(p_6m_31to36)

# 경로를 딕셔너리로 정의
paths = {
    0: path_uav0,
    1: path_uav1,
    2: path_uav2
}

# 각 UAV의 경로 확인
for uav_id, path in paths.items():
    print(f"UAV {uav_id} Path: {path}")

uav_colors = ['pink', 'green', 'blue']

battery_drain_uav1 = 30
battery_charge_uav1 = 30
battery_drain_uav2 = 18
battery_charge_uav2 = 22.5
battery_drain_uav3 = 9
battery_charge_uav3 = 11.25

charging_station = np.array([50, 100], dtype=float)  # 중앙 위치

# vertices 생성 시 검정 박스 영역을 제외하고 생성
vertices = np.array([
    [61.5, 63.4],
    [33.4, 74.9],
    [4.2, 59.6],
    [33.8, 26.9],
    [64.1, 18.4],
    [83.4, 21.7],
    [57.2, 80.9],
    [35.4, 29.4],
    [73.8, 29.6],
    [52.8, 57.4],
    [1.1, 19.9],
    [89.7, 12.9],
    [49.7, 14.6],
    [64.5, 63.3],
    [74.3, 2.8],
    [27.9, 64.7],
    [17.7, 5.2],
    [95.1, 71.4],
    [44.6, 60.5],
    [85.4, 69.1],
    [84.7, 77.8],
    [7.9, 31.6],
    [36.1, 48.6],
    [17.3, 10.1],
    [70.2, 71.9],
    [81.0,  4.5],
    [52.6, 16.7],
    [27.0, 36.4],
    [82.1 , 81.5],
    [8.3 , 67.6],
    [75.6 , 52.4],
    [57.6, 51.2],
    [21.6, 38.1],
    [61.7, 59.6],
    [79.6, 18.1],
    [56.8, 62.8],
    [72.8, 69.9],
    [7.4, 39.3],
    [26.7, 2.0],
    [88.7, 97.4],
    [24.7, 42.5],
    [13.1, 86.4],
    [89.9, 73.4],
    [26.4, 72.0],
    [61.8, 78.4],
    [88.1, 37.3],
    [2.8, 30.4],
    [97.4, 68.9],
    [49.1, 86.8],
    [90.2, 18.4]
])

# 방문 기록과 UAV 위치 초기화
visited = np.zeros((num_uavs, num_vertices), dtype=bool)
uav_positions = np.tile(charging_station, (num_uavs, 1))
visit_counts = np.zeros(num_vertices, dtype=int)
vertex_colors = np.zeros((num_vertices, 3))


# 비행 중 여부와 현재 목표
in_flight = np.zeros(num_uavs, dtype=bool)
current_targets = np.full(num_uavs, -1, dtype=int)

# 배터리 상태 및 위치 초기화
battery_levels = [10.0, 10.0, 46.0]
battery_history = np.zeros((3, frame_number))
battery_history[:, 0] = battery_levels
patches = [[None] * frame_number for _ in range(num_uavs)]
uav_positions = np.array([charging_station] * num_uavs, dtype=float)  # 모든 UAV는 검정 박스 위치에서 시작
uav_colors = sns.husl_palette(n_colors=num_uavs)  # UAV colors

# 방문된 vertices 추적
visited = np.zeros(num_vertices, dtype=bool)
visit_time = np.full(num_vertices, -1, dtype=int)  # 방문 시간 초기화
color_indices = np.zeros(num_vertices, dtype=int)  # 색상 인덱스 초기화

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 7), gridspec_kw={'width_ratios': [1, 0.5]})
plt.subplots_adjust(top=0.75)

# UAV 초기 위치 설정
uav_positions = np.array([charging_station for _ in range(num_uavs)], dtype=float)
# uav_paths = {uav: [uav_positions[uav].copy()] for uav in range(num_uavs)}
# current_targets = [0] * num_uavs  # 모든 UAV의 시작 목표 인덱스를 0으로 설정
uav_paths = {uav: paths[uav] if uav in paths else [] for uav in range(num_uavs)}
current_targets = [0] * num_uavs

# Initialize lines for each UAV
lines = {uav: ax1.plot([], [], color=uav_colors[uav], linewidth=2, label=f'UAV {uav}')[0] for uav in range(num_uavs)}
path_data = {uav: np.array([paths[uav][0]]) for uav in range(num_uavs)}  # Initialize with the first coordinate


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
    fig.text(0.5, 0.90, "Status of Charging Docks (Green: on charge)", fontsize=10, ha='center', va='top', transform=fig.transFigure)

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

def update_uav_target(frame, uav_index):
    if uav_index == 0:
        if frame == 4:
            return 0
        elif frame == 10:
            return len(p_3m_4to6_28to30)
        elif frame == 16:
            return len(p_3m_4to6_28to30) + len(p_3m_10to12_22to24_34to36)
        elif frame == 22:
            return len(p_3m_4to6_28to30) + len(p_3m_10to12_22to24_34to36) + len(p_3m_16to18)
        elif frame == 28:
            return len(p_3m_4to6_28to30) + len(p_3m_10to12_22to24_34to36) + len(p_3m_16to18) + len(p_3m_10to12_22to24_34to36)
        elif frame == 34:
            return len(p_3m_4to6_28to30) + len(p_3m_10to12_22to24_34to36) + len(p_3m_16to18) + len(p_3m_10to12_22to24_34to36) + len(p_3m_4to6_28to30)
    elif uav_index == 1:
        if frame == 5:
            return 0
        elif frame == 14:
            return len(p_5m_5to9_32to36)
        elif frame == 23:
            return len(p_5m_5to9_32to36) + len(p_5m_14to18_23to27)
        elif frame == 32:
            return len(p_5m_5to9_32to36) + len(p_5m_14to18_23to27) + len(p_5m_14to18_23to27)
    elif uav_index == 2:
        if frame == 0:
            return 0
        elif frame == 13:
            return len(p_4m_1to4)
        elif frame == 31:
            return len(p_4m_1to4) + len(p_10m_13to22)
    return None  # 경로를 변경하지 않는 경우


def update_battery_levels(frame, battery_levels):
    new_battery_levels = battery_levels.copy()
    for i in range(len(battery_levels)):
        if frame == 0:
            pass
        else:
            if i == 0:  # UAV1 
                if frame <= 3:
                    battery_levels[i] += battery_charge_uav1
                elif 3 < frame <= 6:
                    battery_levels[i] -= battery_drain_uav1
                elif 6 < frame <= 9:
                    battery_levels[i] += battery_charge_uav1
                elif 9 < frame <= 12:
                    battery_levels[i] -= battery_drain_uav1
                elif 12 < frame <= 15:
                    battery_levels[i] += battery_charge_uav1
                elif 15 < frame <= 18:
                    battery_levels[i] -= battery_drain_uav1
                elif 18 < frame <= 21:
                    battery_levels[i] += battery_charge_uav1
                elif 21 < frame <= 24:
                    battery_levels[i] -= battery_drain_uav1
                elif 24 < frame <= 27:
                    battery_levels[i] += battery_charge_uav1
                elif 27 < frame <= 30:
                    battery_levels[i] -= battery_drain_uav1
                elif 30 < frame <= 33:
                    battery_levels[i] += battery_charge_uav1
                elif 33 < frame <= 36:
                    battery_levels[i] -= battery_drain_uav1
                else:
                    battery_levels[i] += battery_charge_uav1

            elif i == 1: # UAV2
                if frame <= 4:
                    battery_levels[i] += battery_charge_uav2
                elif 5 < frame <= 9:
                    battery_levels[i] -= battery_drain_uav2
                elif 9 < frame <= 13:
                    battery_levels[i] += battery_charge_uav2
                elif 13 < frame <= 18:
                    battery_levels[i] -= battery_drain_uav2
                elif 18 < frame <= 22:
                    battery_levels[i] += battery_charge_uav2
                elif 22 < frame <= 27:
                    battery_levels[i] -= battery_drain_uav2
                elif 27 < frame <= 31:
                    battery_levels[i] += battery_charge_uav2
                else:
                    battery_levels[i] -= battery_drain_uav2

            else:  # UAV3
                if frame <= 4:
                    battery_levels[i] -= battery_drain_uav3
                elif 4 < frame <= 12:
                    battery_levels[i] += battery_charge_uav3
                elif 12 < frame <= 22:
                    battery_levels[i] -= battery_drain_uav3
                elif 22 < frame <= 30:
                    battery_levels[i] += battery_charge_uav3
                else:
                    battery_levels[i] -= battery_drain_uav3

    return new_battery_levels

for frame in range(0, frame_number):
    battery_levels_history = update_battery_levels(frame, battery_levels)
    battery_history[:, frame] = battery_levels
    
   
def update(frame):
    global uav_speed, vertex_colors
    # 그래픽 객체만 초기화    # Iterate over the patches and remove each one
    for patch in ax1.patches:
        patch.remove()

    for line in lines.values():
        line.set_data([], [])  # 기존 선 데이터 초기화 (이전 프레임의 데이터 제거)

    # ax1.clear()
    ax2.clear()
    ax1.set_title(f"Time: {frame} minutes")
    ax2.set_title("Original Battery Status")

    ax1.add_patch(plt.Rectangle(charging_station - 5, 10, 10, color='black'))
        
    # Reset limits after clearing
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, num_uavs)

    # 모든 점이 한번씩 방문되면 색상을 초기화
    if np.all(visit_counts > 0):
        vertex_colors = np.zeros((num_vertices, 3))  # 모든 점을 검정색(RGB: [0, 0, 0])으로 초기화
        visit_counts[:] = 0


    # if frame == 30:
    #     lines.set_data([], [])

    # 각 UAV 업데이트 및 배터리 상태 그리기
    battery_box_height = 1

    # Define triangle size
    triangle_height = 1  # Height of the triangle
    triangle_width = 5   # Base width of the triangle

    # Redraw dynamic text
    text_handle.set_text(f"Number of charging docks = {num_charging_docks}, Number of vehicles = {num_uavs}")

    # 각 UAV 업데이트 및 점 색상 변경
    for i in range(num_uavs):
        # 목표 위치로 이동

        if current_targets[i] < len(paths[i]):
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

                # if np.allclose(uav_positions[i], charging_station):
                # if frame == 30:
                #     lines[i].set_data([], [])
                    
                # # UAV가 충전소에 도달하면 경로 초기화
                if np.allclose(uav_positions[i], charging_station):
                    path_data[i] = np.array([uav_positions[i]])  # 현재 위치를 경로의 첫 좌표로 초기화
                    lines[i].set_data([], [])  # 기존 선 데이터 초기화
                # else:
                #     path_data[i] = np.vstack([path_data[i], uav_positions[i]])

                if current_targets[i] < len(paths[i]) - 1:
                    current_targets[i] += 1  # 다음 목표로 이동

                # 방문한 점의 색상 업데이트
                for v_idx, vertex in enumerate(vertices):
                    if np.allclose(target, vertex):
                        vertex_colors[v_idx] = uav_colors[i]  # UAV 색상으로 업데이트
                        visit_counts[v_idx] += 1  # 방문 횟수 증가

        if np.allclose(uav_positions[i], charging_station):
            path_data[i] = np.array([uav_positions[i]])
            lines[i].set_data([], [])
        
        # 각 점을 그리기 (색상 적용)
    for v_idx, pos in enumerate(vertices):
        ax1.scatter(*pos, color=vertex_colors[v_idx])
        
    # UAV 경로 업데이트
    for i in range(num_uavs):
        path_data[i] = np.vstack([path_data[i], uav_positions[i]])
        lines[i].set_data(path_data[i][:, 0], path_data[i][:, 1])
        # ax1.plot(path_data[i][:, 0], path_data[i][:, 1], color=uav_colors[i])

        # # 선 데이터 업데이트
        # path_data[i] = np.vstack([path_data[i], uav_positions[i]])
        # lines[i].set_data(path_data[i][:, 0], path_data[i][:, 1])

    battery_fill = (battery_levels[i] / 100.0) * 50
    
    # 마지막 프레임인 경우, 다음 프레임의 데이터가 없으므로 현재 프레임과 이전 프레임을 비교
    if frame == frame_number - 1:  # frame_number는 전체 프레임 수
        if battery_history[i, frame] > battery_history[i, frame - 1]:
            # print("green",i, battery_history[i, frame], battery_history[i, frame+1])
            facecolor = 'green'
        else:
            facecolor = 'red'
    else:
        if battery_history[i, frame] > battery_history[i, frame - 1]:
            # print("green",i, battery_history[i, frame], battery_history[i, frame+1])
            facecolor = 'green'  # 충전 중
        else:
            # print("red",i, battery_history[i, frame], battery_history[i, frame+1])
            facecolor = 'red'  # 방전 중
    
    ax2.add_patch(plt.Rectangle((5, i * (battery_box_height + 5)), battery_fill, battery_box_height, facecolor=facecolor, edgecolor='black'))


    ax2.text(60, i * (battery_box_height + 5) + battery_box_height / 2, f'{battery_levels[i]:.1f}%', verticalalignment='center')
    ax2.text(-9, i * (battery_box_height + 5) + battery_box_height / 2, f'UAV {uav_numbers[i]}', verticalalignment='center')

    # Draw UAVs
    ax1.add_patch(plt.Polygon(uav_positions[i] + np.array([[0, 2], [-1, -1], [1, -1]]),
                                closed=True, color=uav_colors[i], edgecolor='black', linewidth=2))

    #여기까지 드론
    
    # Update battery levels based on UAV number and frame
    if frame == 0:
        pass
    else:
        if i == 0:  # UAV1 
            if frame <= 3:
                battery_levels[i] += battery_charge_uav1
            elif 3 < frame <= 6:
                battery_levels[i] -= battery_drain_uav1
            elif 6 < frame <= 9:
                battery_levels[i] += battery_charge_uav1
            elif 9 < frame <= 12:
                battery_levels[i] -= battery_drain_uav1
            elif 12 < frame <= 15:
                battery_levels[i] += battery_charge_uav1
            elif 15 < frame <= 18:
                battery_levels[i] -= battery_drain_uav1
            elif 18 < frame <= 21:
                battery_levels[i] += battery_charge_uav1
            elif 21 < frame <= 24:
                battery_levels[i] -= battery_drain_uav1
            elif 24 < frame <= 27:
                battery_levels[i] += battery_charge_uav1
            elif 27 < frame <= 30:
                battery_levels[i] -= battery_drain_uav1
            elif 30 < frame <= 33:
                battery_levels[i] += battery_charge_uav1
            elif 33 < frame <= 36:
                battery_levels[i] -= battery_drain_uav1
            else:
                battery_levels[i] += battery_charge_uav1

        elif i == 1: # UAV2
            if frame <= 4:
                battery_levels[i] += battery_charge_uav2
            elif 5 < frame <= 9:
                battery_levels[i] -= battery_drain_uav2
            elif 9 < frame <= 13:
                battery_levels[i] += battery_charge_uav2
            elif 13 < frame <= 18:
                battery_levels[i] -= battery_drain_uav2
            elif 18 < frame <= 22:
                battery_levels[i] += battery_charge_uav2
            elif 22 < frame <= 27:
                battery_levels[i] -= battery_drain_uav2
            elif 27 < frame <= 31:
                battery_levels[i] += battery_charge_uav2
            else:
                battery_levels[i] -= battery_drain_uav2

        else:  # UAV3
            if frame <= 4:
                battery_levels[i] -= battery_drain_uav3
            elif 4 < frame <= 12:
                battery_levels[i] += battery_charge_uav3
            elif 12 < frame <= 22:
                battery_levels[i] -= battery_drain_uav3
            elif 22 < frame <= 30:
                battery_levels[i] += battery_charge_uav3
            else:
                battery_levels[i] -= battery_drain_uav3

    # Ensuring battery levels stay within 0-100%
    battery_levels[i] = max(10, min(battery_levels[i], 100))

    # Display battery status
    ax2.add_patch(plt.Rectangle((5, i * (battery_box_height + 5)), 50, battery_box_height, edgecolor='black', facecolor='none'))
    battery_fill = (battery_levels[i] / 100.0) * 50
    # ax2.add_patch(plt.Rectangle((5, i * (battery_box_height + 5)), battery_fill, battery_box_height, facecolor='red' if battery_levels[i] > 50 else 'green'))

    # Define text for battery percentage
    text_x = 60  # x position for battery percentage text
    text_y = i * (battery_box_height + 5) + battery_box_height / 2
    # ax2.text(text_x, text_y, f'{battery_levels[i]:.1f}%', verticalalignment='center')

    # Draw UAV icon to the right of the battery percentage
    icon_x = text_x -1  # x position adjusted to be right of the battery text
    icon_y = text_y

    triangle_points = [(icon_x, icon_y),  # Top point of the triangle
                        (icon_x - triangle_width / 2, icon_y - triangle_height / 2),  # Bottom left point
                        (icon_x - triangle_width / 2, icon_y + triangle_height / 2) ] # Bottom right point    
    ax2.add_patch(plt.Polygon(triangle_points, closed=True, color=uav_colors[i], edgecolor='black', linewidth=1))

    # Update charging dock statuses
    for i, switch in enumerate(switches):
        if i == 0:
            # 첫 번째 스위치는 프레임 1~4와 20~34 사이에 빨간색
            switch.set_facecolor('green' if (frame <= 3 or 5 <= frame <= 15 or 19 <= frame <= 21 or 23 <= frame <= 33) else 'none')
        elif i == 1:
            # 두 번째 스위치는 프레임 5~19 사이에 파란색
            switch.set_facecolor('green' if (frame <=4 or 10 <= frame <= 13 or 19 <= frame <= 22 or 25 <= frame <= 31) else 'none')

    ax1.legend(loc='upper right').set_visible(False)
    # 눈금 제거 및 축 범위 설정
    ax2.set_xlim(0, 70)
    ax2.set_ylim(-1, num_uavs * (battery_box_height + 5))
    ax2.axis('off')  # 축과 눈금 제거

    return [lines[i] for i in range(num_uavs)]

# Create the animation object
ani = animation.FuncAnimation(fig, update, frames=frame_number, init_func=init, interval=50, repeat=False)

# Writer for saving the video
writer = FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)

# Save the animation
ani.save('uav_simulation_test6.mp4', writer=writer)

# Display the plot
plt.show()

# Print the execution time
end_time = time.time()
print("Total Execution Time: {:.2f} minutes".format((end_time - start_time) / 60))
