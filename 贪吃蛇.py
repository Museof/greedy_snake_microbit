from microbit import *
import random, gc, music

# 初始界面
music.play(music.ODE, loop=False, wait=False)
while True:
    display.scroll("A or B")
    if button_a.was_pressed():  # 选A地图
        num = 1
        break
    elif button_b.was_pressed():  # 选B地图
        num = 2
        break

    # 参数设置
# 地图相关
if num == 1:  # A地图
    map = dict()  # 其中元素为(从0开始的row, 从0开始的col): (brightness, type)
    n_row = 5  # 纵向长度
    n_col = 5  # 横向长度
elif num == 2:  # B地图
    map = dict()
    map[3, 3] = ('9', 'obstacle')
    map[3, 6] = ('9', 'obstacle')
    map[6, 3] = ('9', 'obstacle')
    map[6, 6] = ('9', 'obstacle')
    n_row = 10
    n_col = 10

# 游戏参数
game_over = False
game_time = 0
classic_gap = 500
fast_gap = 100
gap = classic_gap  # 每个循环的虚拟时间
score = 0

# 蛇相关
snake = [(n_row // 2, n_col // 2 - 1),
         (n_row // 2, n_col // 2)]  # 前尾后头
direction = 1  # 0表示上，1表示右，2表示下，3表示左
map[(n_row // 2, n_col // 2 - 1)] = ('3', 'snake')
map[(n_row // 2, n_col // 2)] = ('4', 'snake')

# 食物相关
foods = dict()
remain_time = 20000  # 生成食物的停留时间
food_gap = 5000  # 生成食物的间隔时间
food_count = 0

# 开始游戏
while not game_over:
    # 定期生成食物
    if food_count == 0:
        blank_list = [(x, y) for x in range(n_row) for y in range(n_col) \
                      if not (x, y) in map]
        pos = blank_list[random.randint(0, len(blank_list) - 1)]
        map[pos] = ('1', 'food')
        foods[pos] = game_time
    food_count += gap
    if food_count > food_gap:
        food_count = 0

    # 食物定期消失
    for pos in foods:
        if foods[pos] + remain_time < game_time:
            del map[pos]
            del foods[pos]

    # 5×5视野可视化（蛇头亮度为'4'，蛇身为'3'，食物为'1',）
    map_list = [['0' for col in range(5)] for row in range(5)]
    if snake[-1][0] - 2 < 0:
        up_border = 0
        down_border = 4
    elif snake[-1][0] + 2 > n_row - 1:
        down_border = n_row - 1
        up_border = n_row - 5
    else:
        up_border = snake[-1][0] - 2
        down_border = snake[-1][0] + 2
    if snake[-1][1] - 2 < 0:
        left_border = 0
        right_border = 4
    elif snake[-1][1] + 2 > n_col - 1:
        right_border = n_col - 1
        left_border = n_col - 5
    else:
        left_border = snake[-1][1] - 2
        right_border = snake[-1][1] + 2
    for row in range(up_border, down_border + 1):
        for col in range(left_border, right_border + 1):
            if (row, col) in map:
                map_list[row - up_border][col - left_border] = map[(row, col)][0]
    map_str = ':'.join([''.join(row) for row in map_list])
    display.show(Image(map_str))
    sleep(gap)
    game_time += gap

    # 加速与转向
    a = b = False
    if button_a.was_pressed():
        a = True
    if button_b.was_pressed():
        b = True
    if a and b:
        gap = fast_gap
    elif a:
        direction = (direction - 1) % 4
        gap = classic_gap
    elif b:
        direction = (direction + 1) % 4
        gap = classic_gap
    else:
        if not button_a.is_pressed() or not button_b.is_pressed():
            gap = classic_gap

    # 向前移动
    if direction == 0:  # 向上
        front = (snake[-1][0] - 1 if snake[-1][0] != 0 \
                     else n_row - 1,
                 snake[-1][1])
    elif direction == 1:  # 向右
        front = (snake[-1][0],
                 snake[-1][1] + 1 if snake[-1][1] != n_col - 1 \
                     else 0)
    elif direction == 2:  # 向下
        front = (snake[-1][0] + 1 if snake[-1][0] != n_row - 1 \
                     else 0,
                 snake[-1][1])
    else:  # 向左
        front = (snake[-1][0],
                 snake[-1][1] - 1 if snake[-1][1] != 0 \
                     else n_col - 1)
    if (not front in map) or front == snake[0]:
        del map[snake[0]]
        map[snake[-1]] = ('3', 'snake')
        snake.append(front)
        map[front] = ('4', 'snake')
        snake.pop(0)
    elif map[front][1] == 'food':
        map[snake[-1]] = ('3', 'snake')
        snake.append(front)
        map[front] = ('4', 'snake')
        del foods[front]
        music.play(['b'])
        score += 1
    elif map[front][1] in ['snake', 'obstacle']:
        game_over = True
    gc.collect()

# 游戏结束
music.play(music.RINGTONE)
display.scroll(score)