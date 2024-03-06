import random

# Базовый класс для исключений, связанных с игровой доской.
class BoardException(Exception):
    pass
# Исключение, возникающее при попытке выстрелить за пределы игрового поля.
class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы игрового поля!'
# Исключение, возникающее при попытке повторно выстрелить в уже обстрелянную клетку.
class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку!'
# Исключение, связанное с некорректным размещением корабля на игровой доске.
class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Переопределение метода сравнения для точек.
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    # Параметры:
    # bow (Dot): Точка, обозначающая нос корабля.
    # length (int): Длина корабля.
    # orientation (str): Ориентация корабля (‘horizontal’ или ‘vertical’).
    def __init__(self, bow, length, orientation):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    # Возвращает список точек, представляющих корабль на доске.
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 'horizontal':
                cur_x += i
            elif self.orientation == 'vertical':
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots


class Board:
    # Инициализирует объект доски с указанным размером и настройками видимости.
    def __init__(self, hid = False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0

        self.field = [['O']*size for _ in range(size)]
        self.busy = []
        self.ships = []
    # Добавляет корабль на доску.
    def add_ship(self,ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)
    # Отмечает окружающую область вокруг корабля на доске
    def contour(self,ship,verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)
    # Возвращает строковое представление доски для отображения.
    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', 'O')
        return res
    # Проверяет, находится ли координата вне границ доски.
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))
    # Обрабатывает выстрел в указанной координате на доске.
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return True
                else:
                    print('Корабль ранен!')
                    return True

        self.field[d.x][d.y] = 'T'
        print('Мимо!')
        return False
    # Инициализирует игру, сбрасывая список занятых координат.
    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # Абстрактный метод, предназначенный для запроса хода у игрока
    def ask(self):
        raise NotImplementedError()

    # Обрабатывает ход игрока. Запрашивает у игрока координаты и обрабатывает выстрел по противнику.
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    # Генерирует случайные координаты для хода компьютера.
    def ask(self):
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    # Запрашивает у пользователя координаты для хода.
    def ask(self):
        while True:
            coords = input('Ваш ход: ').split()

            if len(coords) != 2:
                print('Неверные данные. Необходимо ввести номер строки и номер столбца.')
                print('Попробуйте еще раз. ')
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа! ')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(random.randint(0, self.size), random.randint(0, self.size)), l,
                            random.choice(['horizontal', 'vertical']))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print()
        print('Добро пожаловать в игру “Морской бой”')
        print()
        print('Необходимо вводить координаты (номер строки и номер столбца) через пробел')


    def loop(self):
        num = 0
        while True:
            print()
            print('Доска пользователя:')
            print(self.us.board)
            print()
            print('Доска компьютера:')
            print(self.ai.board)
            print()
            if num % 2 == 0:
                print('Ходит пользователь!')
                repeat = self.us.move()
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print()
                print('Пользователь выиграл!')
                break

            if self.us.board.count == 7:
                print()
                print('Компьютер выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()

