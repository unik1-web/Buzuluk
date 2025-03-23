class CarIterator:
    def __init__(self):
        self.cars = {
            'У707СА56': ('Мусоровоз', 12550.0),
            'Т945УН56': ('Камаз', 9780.0),
            'М709ВВ116': ('Камаз', 12550.0)
        }
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.cars):
            self.index = 0  # Сбрасываем индекс, чтобы начать заново
        car = self.cars[self.index]
        self.index += 1
        return car

# Пример использования итератора
car_iter = CarIterator()

# Выведем 5 записей, чтобы показать циклическое повторение
for _ in range(5):
    print(next(car_iter))

    # [{'У707СА56': ('Мусоровоз', 12550.0), 'Т945УН56': ('Камаз', 9780.0), 'М709ВВ116': ('Камаз', 12550.0)}]