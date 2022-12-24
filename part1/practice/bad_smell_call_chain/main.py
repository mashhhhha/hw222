# Измените класс Person так, чтобы его методы
# оперировали внутренним состоянием,
# а не использовали цепочку вызовов объектов

class Person:
    def __init__(self, room_number: int, city_population: int):
        self._room_number = room_number
        self._city_population = city_population

    def get_room(self):
        return self._room_number

    def get_population(self):
        return self._city_population