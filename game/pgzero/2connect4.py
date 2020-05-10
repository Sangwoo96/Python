import pgzrun
import numpy as np

WIDTH = 700
HEIGHT = 700
SQUARESIZE = 100
COL = 7
ROW = 6
count = 0
winner = 0
stop = False  # 프로그램 종료
TILE = np.zeros((ROW, COL))  # 타일 리스트 생성


def draw_tile():
    global stop
    # tile view
    for i in range(COL):  # 빈 타일 그리기
        for j in range(ROW):
            screen.draw.filled_rect(
                Rect((i*SQUARESIZE, j*SQUARESIZE), (SQUARESIZE, SQUARESIZE)), 'blue')  # pos, size,color
            screen.draw.filled_circle(
                (i*SQUARESIZE+SQUARESIZE/2, j*SQUARESIZE+SQUARESIZE/2), int(SQUARESIZE/2-5), 'white')  # pos, radius,color

    # 타일 리스를 보고 위치에 말 배치
    for c in range(COL):
        for r in range(ROW):
            if TILE[r][c] == 1:  # 1 -> 빨간말
                screen.draw.filled_circle(
                    (c*SQUARESIZE+SQUARESIZE/2, r*SQUARESIZE+SQUARESIZE/2), int(SQUARESIZE/2-5), 'red')
            elif TILE[r][c] == 2:  # 2 -> 노랑말
                screen.draw.filled_circle(
                    (c*SQUARESIZE+SQUARESIZE/2, r*SQUARESIZE+SQUARESIZE/2), int(SQUARESIZE/2-5), 'yellow')
    if winner == 1:  # 빨간말 승리
        screen.draw.text(
            "red player is win!",
            (20, 620),
            fontname=None,
            fontsize=40,
            color='black',
        )
        stop = True
    if winner == 2:  # 노랑말 승리
        screen.draw.text(
            "yellow player is win!",
            (20, 620),
            fontname=None,
            fontsize=40,
            color='black'
        )
        stop = True


def draw():
    screen.fill((255, 255, 255))
    draw_tile()


def check_winner(color):  # 승자가 존재하는지 확인하는 함수
    for c in range(COL-3):  # 가로를 확인
        for r in range(ROW):
            if TILE[r][c] == color and TILE[r][c+1] == color and TILE[r][c+2] == color and TILE[r][c+3] == color:
                return color

    for c in range(COL):  # 세로를 확인
        for r in range(ROW-3):
            if TILE[r][c] == color and TILE[r+1][c] == color and TILE[r+2][c] == color and TILE[r+3][c] == color:
                return color

    for c in range(COL-3):  # 양의 대각선을 확인
        for r in range(ROW-3):
            if TILE[r][c] == color and TILE[r+1][c+1] == color and TILE[r+2][c+2] == color and TILE[r+3][c+3] == color:
                return color

    for c in range(COL-3):  # 음의 대각선을 확인
        for r in range(3, ROW):
            if TILE[r][c] == color and TILE[r-1][c+1] == color and TILE[r-2][c+2] == color and TILE[r-3][c+3] == color:
                return color


def down(x, y, color):  # 말을 타일의 가장 아래로 떨어뜨려주는 함수
    global count
    for i in range(5, -1, -1):
        if TILE[i][y] == 0:
            TILE[i][y] = color
            return 0  # 말이 올려진 위치를 반환함
    count -= 1  # 꽉 차있는 상태 count를 안해준 것으로 해주기 위해 빼줌


def on_mouse_down(pos, button):  # 마우스 클릭시 타일 배열을 변경시키는 함수
    global count  # mouse click count
    global winner
    if stop == True:  # 승자가 정해진 후 한번더 클릭하면 프로그램 종료
        exit()

    y = int(pos[0]/100)
    x = int(pos[1]/100)
    count += 1
    if count % 2 == 1:  # 놓는 순서 yellow -> red
        down(x, y, 2)
        winner = check_winner(2)  # 이긴 사람이 있는지 확인
    else:
        down(x, y, 1)
        winner = check_winner(1)  # 이긴 사람이 있는지 확인


pgzrun.go()
