from threading import Lock
import numpy
import copy
import utility
from anytree import Node, RenderTree

class rule:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # a list of sequence indexes where this rule appears
        self.sequence_indexes = []
        self.support = 0
        self.confidence = 0

    def __eq__(self, other):
        if numpy.isin(self.x, other.x).all() or numpy.isin(other.x, self.x).all():
            if numpy.isin(self.y, other.y).all() or numpy.isin(other.y, self.y).all():
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
        rules = rule_list()
        for index in self.sequence_indexes:
            x_index = SEQUENCES[index].index(self.x[0])
            # expand to the left
            if x_index > 0:
                string = SEQUENCES[index][x_index - 1]
                if string not in self.x and string not in self.y:
                    new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                    new_rule.x.insert(0, SEQUENCES[index][x_index - 1])
                    new_rule.sequence_indexes.append(index)
                    rules.add(new_rule)
            
            # expand to the right
            if SEQUENCES[index][x_index + len(self.x): x_index + len(self.x) + len(self.y)] != self.y:
                string = SEQUENCES[index][x_index + 1]
                if string not in self.x and string not in self.y:
                    new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                    new_rule.x.append(SEQUENCES[index][x_index + len(self.x)])
                    new_rule.sequence_indexes.append(index)
                    rules.add(new_rule)

        for r in rules:
            r.update_confidence(SEQUENCES)
            r.update_support(SEQUENCES)

        return rules

        return rules
    def expand_y(self, SEQUENCES):
        rules = rule_list()
        for index in self.sequence_indexes:
            y_index = SEQUENCES[index].index(self.y[0])
            # expand to the left
            if y_index < len(SEQUENCES[index])-1:
                string = SEQUENCES[index][y_index + 1]
                if string not in self.x and string not in self.y:
                    new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                    new_rule.y.append(SEQUENCES[index][y_index + 1])
                    new_rule.sequence_indexes.append(index)
                    rules.add(new_rule)
            
            # expand to the right
            if SEQUENCES[index][y_index - len(self.x): y_index-1] != self.x:
                string = SEQUENCES[index][y_index - 1]
                if string not in self.x and string not in self.y:
                    new_rule = rule(copy.copy(self.x), copy.copy(self.y))
                    new_rule.y.insert(0, SEQUENCES[index][y_index-1])
                    new_rule.sequence_indexes.append(index)
                    rules.add(new_rule)

        for r in rules:
            r.update_confidence(SEQUENCES)
            r.update_support(SEQUENCES)

        return rules

class rule_list:
    MIN_CONF = 0.5
    K = 5
    LAMBDA = 3

    def __init__(self):
        self.rules = []

    def __iter__(self):
        for r in self.rules:
            yield r

    def __getitem__(self, item):
        return self.rules[item]

    def __str__(self):
        string = ""
        for i in range(len(self.rules) - self.LAMBDA):
            string += str(self.rules[i])
        return string

    def max_support(self):
        return self.rules[0].support

    def max_confidence(self):
        max_conf = 0
        for r in self.rules:
            if r.confidence > max_conf:
                max_conf = r.confidence
        return max_conf

    def average_support(self):
        sup = 0
        for r in self.rules:
            sup += r.support
        return sup / len(self.rules)

    def average_confidence(self):
        conf = 0
        for r in self.rules:
            conf += r.confidence
        return conf / len(self.rules)

    def add(self, new_rule): 
        if new_rule in self.rules:
            # if the given rule is already listed see if it commes from a different sequence 
            listed_rule = self.rules[self.rules.index(new_rule)]
            for i in new_rule.sequence_indexes:
                if i not in listed_rule.sequence_indexes:
                    listed_rule.sequence_indexes.append(i)
        else:
            self.rules.append(new_rule)

    def filter_top_k(self, SEQUENCES):
        top_k_rules = []
        min_index = 0

        for i in range(len(self.rules)):
            self.rules[i].update_confidence(SEQUENCES)
            self.rules[i].update_support(SEQUENCES)

            if self.rules[i].confidence >= self.MIN_CONF: 

                if len(top_k_rules) < self.K + self.LAMBDA:
                    top_k_rules.append(self.rules[i])
                    if self.rules[i].support < top_k_rules[min_index].support:
                        min_index = len(top_k_rules) - 1
    
                elif self.rules[i].support >= top_k_rules[min_index].support:
                    del top_k_rules[min_index]
                    top_k_rules.append(self.rules[i])
                    min_index = top_k_rules.index(min(top_k_rules))

        # sort in descending order and save
        top_k_rules.sort(reverse=True)
        self.rules = top_k_rules

    def expand_x(self, SEQUENCES):
        tmp = rule_list()
        for r in self.rules:
            tmp1 = r.expand_x(SEQUENCES)
            tmp.merge(tmp1)    
        self.merge(tmp1)
        self.rules.sort(reverse=True)

    def expand_y(self, SEQUENCES):
        tmp = rule_list()
        for r in self.rules:
            tmp1 = r.expand_y(SEQUENCES)
            tmp.merge(tmp1)    
        self.merge(tmp)
        self.rules.sort(reverse=True)

    def merge(self, r_list):
        for r in r_list:
            if r.confidence >= self.MIN_CONF:
                if r not in self.rules:
                    if len(self.rules) < self.K + self.LAMBDA:
                        self.rules.append(r)
                    else:
                        if r > min(self.rules):
                            self.rules.append(r)
                            del self.rules[self.rules.index(min(self.rules))]
