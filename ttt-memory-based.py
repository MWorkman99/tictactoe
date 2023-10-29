import curses, random
import time

p1 = None
p2 = None
log = []

class Board:
    def __init__(self, scr):
        self.clear()
        self._scr = scr
        self.draw()

    def clear(self):
        self._board = list(" " * 9)

    @property
    def board(self):
        return self._board

    def draw(self):
        self._scr.clear()
        b = self.board
        self._scr.addstr(2, 2, "|".join(b[0:3]))
        self._scr.addstr(3, 2, "-+-+-")
        self._scr.addstr(4, 2, "|".join(b[3:6]))
        self._scr.addstr(5, 2, "-+-+-")
        self._scr.addstr(6, 2, "|".join(b[6:9]))
        self._scr.addstr(10, 1, "")

    def move(self, pos, who):
        # pos = 0..8.
        # who = x, o.
        if self._board[pos] != " ":
            raise Exception("Already taken." + str(pos) + " " + str(self._board))
        else:
            self._board[pos] = who
            self.draw()

    def winner(self) -> bool:
        b = self._board
        if b[0] != " " and b[0] == b[1] == b[2]:
            return True
        if b[0] != " " and b[0] == b[4] == b[8]:
            return True
        if b[0] != " " and b[0] == b[3] == b[6]:
            return True
        if b[3] != " " and b[3] == b[4] == b[5]:
            return True
        if b[6] != " " and b[6] == b[7] == b[8]:
            return True
        if b[1] != " " and b[1] == b[4] == b[7]:
            return True
        if b[2] != " " and b[2] == b[5] == b[8]:
            return True

    def full(self) -> bool:
        if not " " in self._board:  # board full, so tie.
            return True
        else:
            return False


class Player:
    def __init__(self, name, xo):
        self._name = name
        # list of positions, assuming taking turns.
        self._brain = {"win": [], "tie": [], "loss": []}
        self._xo = xo

    def rememberGame(self, result, moves):
        global log
        if moves not in self._brain[result]:
            self._brain[result].append(moves)

    @property
    def name(self):
        return self._name

    def move(self, board, move, moves):
        global log

        # first look for a known win.
        for b in self._brain["win"]:
            if move > 1 and b[0 : move - 1] == moves[0 : move - 1]:
                return b[move - 1]
            
        # else look for a known tie
        for b in self._brain["tie"]:
            if move > 1 and b[0 : move - 1] == moves[0 : move - 1]:
                return b[move - 1]

        # otherwise guess
        options = []
        for o in range(0, 9):
            if board[o] == " ":
                options.append(o)
        if len(options) == 0:
            return -1
        return random.choice(options)


def main(stdscr: curses.window):
    global p1, p2
    curses.resizeterm(102, 45)
    stdscr.nodelay(True)

    brd = Board(stdscr)
    p1 = Player("Paul", "x")
    p2 = Player("Ringo", "o")
    xWins = 0
    oWins = 0
    ties = 0

    c = 0
    cnt = 0
    while c != ord("q") and c!= 3 and cnt < 100:
        cnt += 1
        brd.clear()
        stdscr.erase()
        move = 0
        moves = []
        while not brd.winner() and not brd.full():
            #stdscr.erase()
            move += 1
            if move > 10:
                break
            mv = p1.move(brd.board, move, moves)

            if mv < 0:
                p1.rememberGame("tie", moves)
                p2.rememberGame("tie", moves)
                ties += 1
                stdscr.addstr(11, 2, "Current result: Tie")
            else:
                moves.append(mv)
                brd.move(mv, "x")

            if brd.full():
                p1.rememberGame("tie", moves)
                p2.rememberGame("tie", moves)
                ties += 1
                stdscr.addstr(11, 2, "Current result: Tie")
            elif brd.winner():
                p1.rememberGame("win", moves)
                p2.rememberGame("loss", moves)
                xWins += 1
                stdscr.addstr(11, 2, "Current result: X Wins")

            if not brd.winner() and not brd.full():
                move += 1
                mv = p2.move(brd.board, move, moves)

                if mv < 0:
                    p1.rememberGame("tie", moves)
                    p2.rememberGame("tie", moves)
                    ties += 1
                    stdscr.addstr(11, 2, "Current result: Tie")
                else:
                    moves.append(mv)
                    brd.move(mv, "o")

                if brd.full():
                    p1.rememberGame("tie", moves)
                    p2.rememberGame("tie", moves)
                    ties += 1
                    stdscr.addstr(11, 2, "Current result: Tie")
                elif brd.winner():
                    p1.rememberGame("loss", moves)
                    p2.rememberGame("win", moves)
                    oWins += 1
                    stdscr.addstr(11, 2, "Current result: O Wins")
            time.sleep(0.1)
            stdscr.refresh()

        # draw status screen
        stdscr.addstr(8, 2, "xWins = " + str(xWins))
        stdscr.addstr(9, 2, "oWins = " + str(oWins))
        stdscr.addstr(10, 2, "Ties = " + str(ties))

        stdscr.addstr(12, 2, "X's Brain for Wins")
        l = sorted(p1._brain["win"], key=len)
        for i in range(0, min(7, len(l))):
            stdscr.addstr(13 + i, 2, " " + str(l[i]))

        stdscr.addstr(22, 2, "O's Brain for Wins")
        l = sorted(p2._brain["win"], key=len)
        for i in range(0, min(7, len(l))):
            stdscr.addstr(23 + i, 2, " " + str(l[i]))

        # Wait for user input
        stdscr.addstr(31, 2, '"q" to quit.')
        c = stdscr.getch()
        time.sleep(0.1)
        stdscr.refresh()


try:
    curses.wrapper(main)
except Exception as e:
    print(str(e))

# print("") 
# print("")
# print(p1._brain)
# print(p2._brain)
for l in log:
    print(l)
