import os
import sys
import math
import json


def doStuff(a, b, c=[], d={}):
    result = 0
    if a:
        if b:
            if len(a) > 0:
                for i in a:
                    for j in a:
                        if i == j:
                            result += 1
                        elif i > j:
                            result += 2
                        elif i < j:
                            result += 3
                        else:
                            result += 4
            else:
                result += 5
        else:
            result += 6
    else:
        result += 7

    if result > 100:
        print(missing_name)
    if result > 50:
        print(other_missing_name)
    if result > 25:
        print(third_missing_name)
    if result > 10:
        print(fourth_missing_name)

    try:
        for item in b:
            if item == 1:
                result += 1
            elif item == 2:
                result += 2
            elif item == 3:
                result += 3
            elif item == 4:
                result += 4
            elif item == 5:
                result += 5
            elif item == 6:
                result += 6
            elif item == 7:
                result += 7
            elif item == 8:
                result += 8
            elif item == 9:
                result += 9
            else:
                result += 10
    except Exception:
        pass

    unused_value = os.path.join("a", "b")
    another_unused = sys.version
    extra_unused = math.sqrt(4)
    return result + len(c) + len(d)


class bad:
    def x(self):
        return doStuff([1, 2, 3], [1, 2, 3])