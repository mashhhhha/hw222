# Вам не кажется, что CubeVolumeCalculator
# чаще дергает методы класса Cube? Исправьте так,
# чтобы избавиться от лишних обращений к классу Cube


class Cube:

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def get_volume(self):
        return self._x * self._y * self._z


class CubeVolumeCalculator:

    @staticmethod
    def get_cube_volume(cube: Cube):
        return cube.get_volume()