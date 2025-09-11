
class UserData:
    def __init__(self, constellation):
        self.constellation = constellation
        self.dish = None
        self.gs = []
        self.descriptor_path = []
        self.flags = {}
        self.saved_measurements = {}
        self.sid = 0
        self.emulator = False
    def set_sid(self, sid):
        self.sid = sid
    def get_sid(self):
        return self.sid
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
    def set_gs(self, gs):
        self.gs = gs
    def get_gs(self):
        return self.gs
    def push_gs(self, gs):
        self.gs.extend(gs)
    def set_descriptor_path(self, path):
        self.descriptor_path = path
    def get_descriptor_path(self):
        return self.descriptor_path
    def has_path(self):
        return self.descriptor_path != []
    def get_descriptor_path(self):
        return self.descriptor_path
    def has_connection(self):
        if len(self.descriptor_path) < 3:
            return False
        else:
            return self.descriptor_path[0].startswith("DISH") and self.descriptor_path[-1].startswith("GS")
    def is_flag(self, flagname):
        if flagname in self.flags:
            return self.flags[flagname]
        return False
    def set_flag(self, flagname):
        self.flags[flagname] = True
    def remove_flag(self, flagname):
        self.flags[flagname] = False
    def get_saved_measurements(self):
        return self.saved_measurements
    def add_measurements(self, measurements: dict):
        for field in measurements:
            if field in self.saved_measurements:
                self.saved_measurements[field].append(measurements[field])
            else:
                self.saved_measurements[field] = [measurements[field]]
    def set_emulator(self, is_emulator):
        self.emulator = is_emulator
    def is_emulator(self):
        return self.emulator
        