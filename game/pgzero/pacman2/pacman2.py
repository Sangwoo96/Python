import pgzrun
import gameinput
import gamemaps
from random import randint
from datetime import datetime
WIDTH = 600
HEIGHT = 660

player = Actor("pacman_o")  # Load in the player Actor image
player.score = 0
player.lives = 3
level = 0
SPEED = 3


def draw():  # Pygame Zero draw function
    global pacDots, player
    screen.blit('header', (0, 0))
    screen.blit('colourmap', (0, 80))
    pacDotsLeft = 0
    for a in range(len(pacDots)):
        if pacDots[a].status == 0:
            pacDots[a].draw()
            pacDotsLeft += 1
        if pacDots[a].collidepoint((player.x, player.y)):
            if pacDots[a].status == 0:
                if pacDots[a].type == 2:
                    for g in range(len(ghosts)):
                        ghosts[g].status = 1200
                else:
                    player.score += 10
            pacDots[a].status = 1
    if pacDotsLeft == 0:
        player.status = 2
    drawGhosts()
    getPlayerImage()
    player.draw()
    drawLives()
    screen.draw.text("LEVEL "+str(level), topleft=(10, 10), owidth=0.5,
                     ocolor=(0, 0, 255), color=(255, 255, 0), fontsize=40)
    screen.draw.text(str(player.score), topright=(590, 20), owidth=0.5, ocolor=(
        255, 255, 255), color=(0, 64, 255), fontsize=60)
    if player.status == 3:
        drawCentreText("GAME OVER")
    if player.status == 2:
        drawCentreText("LEVEL CLEARED!\nPress Enter or Button A\nto Continue")
    if player.status == 1:
        drawCentreText("CAUGHT!\nPress Enter or Button A\nto Continue")


def drawCentreText(t):  # 중앙에 텍스트 출력
    screen.draw.text(t, center=(300, 434), owidth=0.5, ocolor=(
        255, 255, 255), color=(255, 64, 0), fontsize=60)


def update():  # Pygame Zero update function
    global player, moveGhostsFlag, ghosts
    if player.status == 0:
        if moveGhostsFlag == 4:
            moveGhosts()
        for g in range(len(ghosts)):
            if ghosts[g].status > 0:
                ghosts[g].status -= 1
            if ghosts[g].collidepoint((player.x, player.y)):
                if ghosts[g].status > 0:
                    player.score += 100
                    animate(ghosts[g], pos=(290, 370), duration=1/SPEED,
                            tween='linear', on_finished=flagMoveGhosts)
                else:
                    player.lives -= 1
                    sounds.pac2.play()
                    if player.lives == 0:
                        player.status = 3
                        music.fadeout(3)
                    else:
                        player.status = 1
        if player.inputActive:
            gameinput.checkInput(player)
            gamemaps.checkMovePoint(player)
            if player.movex or player.movey:
                inputLock()
                sounds.pac1.play()
                animate(player, pos=(player.x + player.movex, player.y + player.movey),
                        duration=1/SPEED, tween='linear', on_finished=inputUnLock)
    if player.status == 1:
        i = gameinput.checkInput(player)
        if i == 1:
            player.status = 0
            player.x = 290
            player.y = 570
    if player.status == 2:
        i = gameinput.checkInput(player)
        if i == 1:
            init()
    # print(player.movex, " " , player.movey)


def init():
    global player, level
    initDots()
    initGhosts()
    player.x = 290
    player.y = 570
    player.status = 0
    inputUnLock()
    level += 1
    music.play("pm1")
    music.set_volume(0.2)


def drawLives():
    for l in range(player.lives):
        screen.blit("pacman_o", (10+(l*32), 40))


def getPlayerImage():
    global player
    dt = datetime.now()
    a = player.angle
    tc = dt.microsecond % (500000/SPEED)/(100000/SPEED)
    if tc > 2.5 and (player.movex != 0 or player.movey != 0):
        if a != 180:
            player.image = "pacman_c"
        else:
            player.image = "pacman_cr"
    else:
        if a != 180:
            player.image = "pacman_o"
        else:
            player.image = "pacman_or"
    player.angle = a


def drawGhosts():
    for g in range(len(ghosts)):
        if ghosts[g].x > player.x:
            if ghosts[g].status > 200 or (ghosts[g].status > 1 and ghosts[g].status % 2 == 0):
                ghosts[g].image = "ghost5"
            else:
                ghosts[g].image = "ghost"+str(g+1)+"r"
        else:
            if ghosts[g].status > 200 or (ghosts[g].status > 1 and ghosts[g].status % 2 == 0):
                ghosts[g].image = "ghost5"
            else:
                ghosts[g].image = "ghost"+str(g+1)
        ghosts[g].draw()


def moveGhosts():
    global moveGhostsFlag
    global nd  # 고스트가 벽에 몰렸을 때 플레이어 방향으로 오지 않게 하기 위한 변수
    dmoves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    moveGhostsFlag = 0
    for g in range(len(ghosts)):
        nd = -1
        dirs = gamemaps.getPossibleDirection(ghosts[g])
        if(ghosts[g].status > 0):  # 사탕을 먹었을 때
            if inTheCentre(ghosts[g]):
                ghosts[g].dir = 3
            else:
                avoidPlayer(g, dirs)
        else:  # 사탕을 안먹었을 때
            if inTheCentre(ghosts[g]):
                ghosts[g].dir = 3
            else:
                # 전술 : 0번과 3번은 따라다니고 1번과 2번은 플레이어가 가는 길목에 잠복 후 포위하면 따라감
                if g == 0:  # 0번 고스트는 플레이어를 따라감
                    followPlayer(g, dirs)
                if g == 1:  # 1번 고스트는 플레이러를 일정 거리까지 잠복하다 가까워지면 따라간다
                    ambushPlayer(g, dirs, 0, 2, 1, 3)
                # 2번 고스트는 플레이러를 일정 거리까지 1번 고스트와 반대 방향으로 잠복하다 가까워지면 따라간다
                if g == 2:
                    ambushPlayer(g, dirs, 0, 2, 3, 1)  # 0231
                if g == 3:  # 3번 고스트는 플레이어를 따라감
                    followPlayer(g, dirs)
        if dirs[ghosts[g].dir] == 0 or randint(0, 50) == 0:
            d = -1
            while d == -1:
                rd = randint(0, 3)
                if aboveCentre(ghosts[g]) and rd == 1:
                    rd = 0
                if nd == -1:
                    if dirs[rd] == 1:
                        d = rd
                # 플레이어가 오는 반대방향으로 길이 없을 때 nd(플레이어가 오는 방향)을 제외한 갈 수 있는 방향을 찾아줌
                else:
                    if rd != nd and dirs[rd] == 1:
                        d = rd
            ghosts[g].dir = d
        animate(ghosts[g], pos=(ghosts[g].x + dmoves[ghosts[g].dir][0]*20, ghosts[g].y +
                                dmoves[ghosts[g].dir][1]*20), duration=1/SPEED, tween='linear', on_finished=flagMoveGhosts)


def avoidPlayer(g, dirs):  # 플레이어를 피하는 함수
    global player
    global nd  # 고스트가 벽에 몰렸을 때 플레이어 방향으로 오지 않게 하기 위한 변수
    xm = ghosts[g].x - player.x
    ym = ghosts[g].y - player.y
    if ghosts[g].x == player.x and ym < 90 and ym > -90:
        if player.movey > 0:
            ghosts[g].dir = 1
            nd = 3
        elif player.movey == 0:
            if player.y > ghosts[g].y:
                ghosts[g].dir = 3
            else:
                ghosts[g].dir = 1
        else:
            ghosts[g].dir = 3
            nd = 1
    elif ghosts[g].y == player.y and xm < 90 and xm > -90:
        if player.movex > 0:
            ghosts[g].dir = 0
            nd = 2
        elif player.movex == 0:
            if player.x > ghosts[g].x:
                ghosts[g].dir = 2
            else:
                ghosts[g].dir = 0
        else:
            ghosts[g].dir = 2
            nd = 0


def followPlayer(g, dirs):  # 플레이어를 따라가는 함수
    d = ghosts[g].dir
    if d == 1 or d == 3:
        if player.x > ghosts[g].x and dirs[0] == 1:
            ghosts[g].dir = 0
        if player.x < ghosts[g].x and dirs[2] == 1:
            ghosts[g].dir = 2
    if d == 0 or d == 2:
        if player.y > ghosts[g].y and dirs[1] == 1 and not aboveCentre(ghosts[g]):
            ghosts[g].dir = 1
        if player.y < ghosts[g].y and dirs[3] == 1:
            ghosts[g].dir = 3


def ambushPlayer(g, dirs, d0, d1, d2, d3):  # 플레이어를 잠복하다 따라가는 함수
    global player
    d = ghosts[g].dir
    xm = ghosts[g].x - player.x
    ym = ghosts[g].y - player.y
    if -115 < xm < 115 and -115 < ym < 115:  # 일정 거리 안에 플레이어가 있으면 따라옴
        if d == 1 or d == 3:
            if player.x > ghosts[g].x and dirs[0] == 1:
                ghosts[g].dir = 0
            if player.x < ghosts[g].x and dirs[2] == 1:
                ghosts[g].dir = 2
        if d == 0 or d == 2:
            if player.y > ghosts[g].y and dirs[1] == 1 and not aboveCentre(ghosts[g]):
                ghosts[g].dir = 1
            if player.y < ghosts[g].y and dirs[3] == 1:
                ghosts[g].dir = 3
    else:  # 일정 거리 이상이면 플레이어를 잠복함
        if player.movex > 0 and dirs[0] == 1:
            ghosts[g].dir = d0
        if player.movex < 0 and dirs[2] == 1:
            ghosts[g].dir = d1

        if player.movey > 0 and dirs[1] == 1 and not aboveCentre(ghosts[g]):
            ghosts[g].dir = d2
        if player.movey < 0 and dirs[3] == 1:
            ghosts[g].dir = d3


def inTheCentre(ga):
    if ga.x > 220 and ga.x < 380 and ga.y > 320 and ga.y < 420:
        return True
    return False


def aboveCentre(ga):
    if ga.x > 220 and ga.x < 380 and ga.y > 300 and ga.y < 320:
        return True
    return False


def flagMoveGhosts():
    global moveGhostsFlag
    moveGhostsFlag += 1


def ghostCollided(ga, gn):
    for g in range(len(ghosts)):
        if ghosts[g].colliderect(ga) and g != gn:
            return True
    return False


def initDots():
    global pacDots
    pacDots = []
    a = x = 0
    while x < 30:
        y = 0
        while y < 29:
            d = gamemaps.checkDotPoint(10+x*20, 10+y*20)
            if d == 1:                                     # dot그리기 type 1 일반 사탕
                pacDots.append(Actor("dot", (10+x*20, 90+y*20)))
                pacDots[a].status = 0  # status 0 은 안먹힌 상태 1은 먹힌 상태
                pacDots[a].type = 1
                a += 1
            if d == 2:  # type 2 특수 사탕
                pacDots.append(Actor("power", (10+x*20, 90+y*20)))
                pacDots[a].status = 0
                pacDots[a].type = 2
                a += 1
            y += 1
        x += 1


def initGhosts():
    global ghosts, moveGhostsFlag
    moveGhostsFlag = 4
    ghosts = []
    g = 0
    while g < 4:
        ghosts.append(Actor("ghost"+str(g+1), (270+(g*20), 370)))
        ghosts[g].dir = randint(0, 3)
        ghosts[g].status = 0
        g += 1


def inputLock():
    global player
    player.inputActive = False


def inputUnLock():
    global player
    player.movex = player.movey = 0
    player.inputActive = True


init()
pgzrun.go()
