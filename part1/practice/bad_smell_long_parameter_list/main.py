# У нас есть какой-то юнит, которому мы в параметры передаем
# - наше игровое поле
# - х координату
# - у координату
# - направление смещения
# - летит ли он
# - крадется ли он
# - скорость
# В этом примере есть сразу несколько запахов плохого кода. Исправьте их
#   (длинный метод, длинный список параметров)


class UpdatedUnit:
    def __init__(self, field, x_coord: int, y_coord: int, state: str, speed=1 ):
        self.field = field
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.state = state
        self.speed = speed

    def _get_speed(self):
        if self.state.lower() == 'fly':
            return self.speed * 1.2

        elif self.state.lower() == 'crawl':
            return self.speed * 0.5

        else:
            raise ValueError('Неопределенный метод передвижения')

    def move(self, direction: str):
        speed = self._get_speed()

        if direction.lower() == 'up':
            self.y_coord += speed
        elif direction.lower() == 'down':
            self.y_coord -= speed
        elif direction.lower() == 'left':
            self.x_coord -= speed
        elif direction.lower() == 'right':
            self.x_coord += speed
        else:
            raise ValueError('Неопределенное направление')