import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
# import matplotlib.colors as mcolors
# import random
import time

# Example path data for each UAV
paths = {
    0: [(50,100), (10, 10), (20, 20), (30, 40), (40, 60), (50, 80)],
    1: [(50,100), (15, 10), (25, 20), (35, 40), (45, 60), (55, 80)],
    2: [(50,100), (10, 15), (20, 25), (30, 45), (40, 65), (50, 85)],
    3: [(50,100), (5, 10), (15, 20), (25, 40), (35, 60), (45, 80)]
}


# 시간 측정 시작
start_time = time.time()

# 초기 설정 변경
num_uavs = 4
num_charging_docks = 2
num_vertices = 50  # 노드 수
frame_number = 34  # 프레임 수
uav_speed = 15
battery_drain = 4.5
battery_charge = 6.5
charging_station = np.array([50, 100], dtype=float)  # 중앙 위치
magma_colors = plt.get_cmap('magma')(np.linspace(0, 1, 100))

# vertices 생성 시 검정 박스 영역을 제외하고 생성
vertices = np.array([np.random.rand(2) * 100 for _ in range(num_vertices) if not (45 <= np.random.rand(2)[0] * 100 <= 55 and 45 <= np.random.rand(2)[1] * 100 <= 55)])

# # UAV별 방문할 vertices 분배, vertices 개수를 초과하지 않도록 확인
uav_routes = np.array_split(np.random.permutation(len(vertices)), num_uavs)

# 배터리 상태 및 위치 초기화
battery_levels = np.full(num_uavs, 100.0)
uav_positions = np.array([charging_station] * num_uavs, dtype=float)  # 모든 UAV는 검정 박스 위치에서 시작
uav_colors = [sns.husl_palette(n_colors=num_uavs)[i] for i in range(num_uavs)]  # 각 UAV에 랜덤 색상 할당

# 방문된 vertices 추적
visited = np.zeros(num_vertices, dtype=bool)
visit_time = np.full(num_vertices, -1, dtype=int)  # 방문 시간 초기화
color_indices = np.zeros(num_vertices, dtype=int)  # 색상 인덱스 초기화

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={'width_ratios': [1.5, 1]})
plt.subplots_adjust(top=0.75)

# 색상 막대 추가
sm = plt.cm.ScalarMappable(cmap='magma', norm=plt.Normalize(0, 100))
sm.set_array([])
plt.colorbar(sm, ax=ax1, orientation='vertical', label='Time Since Visit', pad=0.1)

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
    ax1.add_patch(plt.Rectangle(charging_station - 5, 10, 10, color='black'))  # 검정 박스 그리기

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
    
    return fig,

def update(frame):
    ax1.clear()
    ax2.clear()
    ax1.set_title(f"Time: {frame} seconds")
    ax2.set_title("Current Battery Status")
    ax1.add_patch(plt.Rectangle(charging_station - 5, 10, 10, color='black'))

    # Reset limits after clearing# 축 레이블 설정
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_xlim(-5, 105)
    ax1.set_ylim(-5, 110)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, num_uavs)

    # Vertices 그리기
    for i, pos in enumerate(vertices):
        if visited[i]:
            # 방문된 시간에 따라 색상 결정
            # 최근 방문 시간을 기준으로 색상을 선택합니다.
            color_index = max(0, color_indices[i] - 3 * frame + 3 * visit_time[i])  # 색상 인덱스 감소
            ax1.scatter(*pos, color=magma_colors[color_index])
        else:
            ax1.scatter(*pos, color='black')


    # 각 UAV 업데이트 및 배터리 상태 그리기
    battery_box_height = 1
    # Define triangle size
    triangle_height = 1  # Height of the triangle
    triangle_width = 5   # Base width of the triangle

    # Redraw dynamic text
    text_handle.set_text(f"Number of charging docks = {num_charging_docks}, Number of vehicles = {num_uavs}")
    
    for i in range(num_uavs):
        # 여기서부터
        index = frame % len(uav_routes[i])  # 현재 프레임에 대한 인덱스 계산
        current_target = vertices[uav_routes[i][index]]  # 이 부분에서 에러 발생 가능성 감소
        direction = current_target - uav_positions[i]
        distance = np.linalg.norm(direction)

        if distance > uav_speed:
            direction = direction / distance * uav_speed

        uav_positions[i] += direction

        # UAV 그리기 (색상 및 테두리 추가)
        ax1.add_patch(plt.Polygon(uav_positions[i] + np.array([[0, 2], [-1, -1], [1, -1]]),
                                closed=True,
                                color=uav_colors[i],
                                edgecolor='black',
                                linewidth=2))  # 테두리 두께를 2로 설정
        
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
        ax2.text(-5, i * (battery_box_height + 5) + battery_box_height / 2, f'UAV {i+1}', verticalalignment='center')

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

    # Correct handling of switches based on the charging logic
    for i in range(num_charging_docks):
        if (frame <= 14 or frame > 20) and frame <= 34:
            fill_color = 'red'  # On state
        else:
            fill_color = 'none'  # Off state
        switches[i].set_facecolor(fill_color)

    ax1.legend()
    # 눈금 제거 및 축 범위 설정
    ax2.set_xlim(0, 70)
    ax2.set_ylim(-1, num_uavs * (battery_box_height + 5))
    ax2.axis('off')  # 축과 눈금 제거

ani = animation.FuncAnimation(fig, update, frames=frame_number, init_func=init, repeat=False)
plt.show()

# 시간 측정 종료 및 출력
end_time = time.time()
print("Total Execution Time: {:.2f} seconds".format(end_time - start_time))
