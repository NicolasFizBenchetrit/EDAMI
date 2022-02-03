import numpy
import utility
import copy

class rule:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # a list of sequence indexes where this rule appears
        self.sequence_indexes = []
        self.support = 0
        self.confidence = 0

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            if self.support == other.support and self.confidence == other.confidence:
                return True
        return False

    def __str__(self):
        string = str(self.x) + " -> " + str(self.y) + "\n"
        string += "Sequences[" + str(len(self.sequence_indexes)) + "]: " + str(self.sequence_indexes) + "\n"
        string += "Relative Support: " + str(self.support) + "\n"
        string += "Confidence: " + str(self.confidence) + "\n"
        string += "\n"
        return string

    def __lt__(self, other):
        if self.support < other.support:
            return True
        elif self.support == other.support:
            return len(self.x) + len(self.y) < len(other.x) + len(other.y)
        return False

    def __ge__(self, other):
        if self.support >= other.support:
            return True
        elif self.support == other.support:
            return len(self.x) + len(self.y) >= len(other.x) + len(other.y)
        return False

    def update_support(self, SEQUENCES):
        self.support = (len(self.sequence_indexes) / len(SEQUENCES))

    def update_confidence(self, SEQUENCES):
        count = 0
        for seq in SEQUENCES:
            collision = 0
            # check that self.x is a sub array of seq
            if numpy.isin(self.x, seq).any():
                count += 1
        self.confidence = len(self.sequence_indexes) / count

    def expand_x(self, SEQUENCES):
        rules = []
        for index in self.sequence_indexes:
            x_index = utility.find_sub_array_index(SEQUENCES[index], self.x)
            # expand to the left
            if x_index > 0:
                new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                new_rule.x.insert(0, SEQUENCES[index][x_index - 1])
                new_rule.sequence_indexes.append(index)
                rules.append(new_rule)
            
            # expand to the right
            if SEQUENCES[index][x_index + len(self.x): x_index + len(self.x) + len(self.y)] != self.y:
                new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                new_rule.x.append(SEQUENCES[index][x_index + len(self.x)])
                new_rule.sequence_indexes.append(index)
                rules.append(new_rule)

        return rules
