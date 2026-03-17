class Cache:
    def __init__(self):
        self.value = {}

    def add(self, key, value):
        self.value[key] = value


class Logger:
    def __init__(self):
        self.last = None

    def write(self, message):
        self.last = message


def calculate_total(items):
    total = 0
    for price in items:
        total += price
    return total