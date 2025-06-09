
class UserData:
    def __init__(self, constellation):
        self.constellation = constellation
        self.dish = None
    def get_constellation(self):
        return self.constellation
    def set_constellation(self, constellation):
        self.constellation = constellation
    def set_dish(self, dish):
        self.dish = dish
    def get_dish(self):
        return self.dish
    def has_dish(self):
        return self.dish != None