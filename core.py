import os


def prefixfn(string, _, new):
    return new + string


def suffixfn(string, _, new):
    before, sep, after = string.partition('.')
    return ''.join([before, new, '.', after])


def insertfn(string, substring, new):
    if not substring or substring not in string:
        return string
    before, sep, after = string.partition(substring)
    return ''.join([before, new, sep, after])


def appendfn(string, substring, new):
    if not substring or substring not in string:
        return string
    before, sep, after = string.partition(substring)
    return ''.join([before, sep, new, after])


def changefn(string, substring, replacement):
    if not substring or substring not in string:
        return string
    before, sep, after = string.partition(substring)
    return ''.join([before, replacement, after])


def listdir(path):
    os.chdir(path)
    return [name for name in os.listdir() if not os.path.isdir(name)]


def rename(lst):
    count = 0
    for (src, dest) in lst:
        if src != dest:
            os.replace(src, dest)
            count += 1
    return count


class Selection:
    def __init__(self, filenames):
        self.entries = [[name] for name in filenames]
        self.stack = [list(range(len(self.entries)))]

    def clear(self):
        self.stack = [list(range(len(self.entries)))]

    def active(self):
        return self.stack[-1]

    def tighten(self, pattern):
        current = self.active()
        new = [i for i in current if pattern in self.entries[i][-1]]
        if current != new:
            self.stack.append(new)

    def loosen(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def peek(self):
        result = []
        for i in self.active():
            entry = self.entries[i]
            result.append((entry[0], entry[-1]))
        return result

    def transform(self, fn):
        for i in self.active():
            entry = self.entries[i]
            entry.append(fn(entry[-1]))

    def rollback(self):
        for i in self.active():
            entry = self.entries[i]
            if len(entry) > 1:
                entry.pop()
