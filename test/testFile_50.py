import os
import sys


def helper(data, default=[]):
    total = 0
    if data:
        for item in data:
            if isinstance(item, int):
                if item > 0:
                    total += item
                elif item == 0:
                    total += 0
                elif item < -10:
                    total -= item * 2
                else:
                    total -= item
            elif isinstance(item, str):
                try:
                    total += int(item)
                except Exception:
                    pass
            elif isinstance(item, float):
                total += int(item)
            else:
                total += 1
    temp_value = 99
    extra_value = "debug"
    return total + len(default)


class manager:
    def run(self, items):
        return helper(items)