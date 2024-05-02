class DictPlus(dict):
    _MISSING = object()

    def get_or_add(self, key, func):
        value = self.get(key, self.__class__._MISSING)
        if value is self.__class__._MISSING:
            value = func()
            self[key] = value
        return value
