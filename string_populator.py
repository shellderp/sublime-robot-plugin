from robot.parsing.populators import FromFilePopulator

class FromStringPopulator(FromFilePopulator):
    def __init__(self, datafile, lines):
        super(FromStringPopulator, self).__init__(datafile)
        self.lines = lines

    def readlines(self):
        return self.lines

    def close(self):
        pass

    def _open(self, path):
        return self
