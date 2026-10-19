class SymbolTable:
    def __init__(self,capacity = 101):
        self.capacity = capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self.entries = []
        self.size = 0

    def hash(self,kind,value):
        """ Calculate a hash index for a symbol"""
        key = f"{kind}:{value}"
        hash_value = 0

        for character in key:
            hash_value = (hash_value * 31 + ord(character)) % self.capacity

        return hash_value


    def search(self,kind,value):
        """ Returns the position of the symbol or None if it does not exist"""
        index = self.hash(kind,value)

        for entry in self.buckets[index]:
            if entry["kind"] == kind and entry["value"] == value:
                return entry["position"]

        return None

    def insert(self,kind,value):
        """Inserts a symbol into the symbol table or returns its existing position"""
        existing_position=self.search(kind,value)
        if existing_position is  not None:
            return existing_position

        position = self.size
        entry={"position":position,"kind":kind,"value":value}
        index = self.hash(kind,value)

        self.buckets[index].append(entry)
        self.entries.append(entry)
        self.size += 1
        return position

    def get_entries(self):
        return self.entries.copy()

    def __len__(self):
        return self.size