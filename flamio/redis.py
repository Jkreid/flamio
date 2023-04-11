
class Redis:
    
    def __init__(self, host, port, db=0) -> None:
        self._cache: dict = {}
    
    def hset(self, key, value, number):
        if key not in self._cache:
            self._cache[key] = {}
        self._cache[key][value] = str(number).encode()
    
    def hget(self, key, value):
        if key in self._cache and value in self._cache[key]:
            return self._cache[key][value]
    
    def hmset(self, key, values):
        for v,n in values.items():
            self.hset(key, v, n)
    
    def hmget(self, key, *values):
        return [self._cache[key][v] if v in self._cache else None for v in values]
    
    def hgetall(self, key):
        return self._cache[key]

    def delete(self, key):
        del self._cache[key]
    
    def ping(self):
        pass
