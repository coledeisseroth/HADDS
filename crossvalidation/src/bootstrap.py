import sys
import os
from collections import defaultdict
import random
import math

def assign_groups(n, ngroups):
    lis = [i for i in range(n)]
    random.shuffle(lis)
    groupsize = int(math.ceil(float(n) / float(ngroups)))
    groups = []
    for i in range(ngroups - 1):
        groups.append(lis[groupsize * i:groupsize * (i+1)])
    groups.append(lis[groupsize * (ngroups-1):])
    print groups
    return groups
    

def extract_data(datafile):
    feature_table = {}
    for line in open(datafile):
        line = line.strip().split("\t")
        feature = line[0]
        feature_table[feature] = line[1:]
    return feature_table

def assign_weight(freq):
    if freq == 1: return 1
    if freq > 0.75: return 0.75
    if freq > 0.5: return 0.5
    if freq > 0.25: return 0.25
    return 0

def train(feature_table, groups, test):
    feature_to_weight = {}
    for feature in feature_table.keys():
        n = 0
        pos = 0
        for i in range(len(groups)):
            if i == test: continue
            for case in groups[i]:
                n += 1
                if feature_table[feature][case] == "yes": pos += 1
        freq = float(pos) / float(n)
        feature_to_weight[feature] = assign_weight(freq)
    return feature_to_weight

def max_score(feature_to_weight):
    returnScore = 0
    for feature in feature_to_weight.keys(): returnScore += feature_to_weight[feature]
    return returnScore

def calculate_score(feature_table, feature_to_weight, case):
    score = 0
    for feature in feature_table.keys():
        if feature_table[feature][case] == "yes": score += feature_to_weight[feature]
    return math.ceil(score * 10 / max_score(feature_to_weight))

def test(feature_table, groups, testg, feature_to_weight):
    scores = []
    for case in groups[testg]:
        scores.append(str(case + 1) + "\t" + str(testg + 1) + "\t" + str(calculate_score(feature_table, feature_to_weight, case)))
    return scores

def main(datafile, obligatory_test, ngroups=2):
    random.seed(12345)
    feature_table = extract_data(datafile)
    nonHADDS_table = extract_data(obligatory_test)
    nTest = len(nonHADDS_table[nonHADDS_table.keys()[0]])
    n = len(feature_table[feature_table.keys()[0]])
    groups = assign_groups(n, ngroups)
    for testg in range(ngroups):
        feature_to_weight = train(feature_table, groups, testg)
        for entry in test(feature_table, groups, testg, feature_to_weight):
            print entry
        for entry in test(nonHADDS_table, [range(len(nonHADDS_table[nonHADDS_table.keys()[0]]))], 0, feature_to_weight):
            print "TESTEE-" + str(testg + 1) + "-" + entry


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

