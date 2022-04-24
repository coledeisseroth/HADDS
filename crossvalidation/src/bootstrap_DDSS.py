import sys
import os
from collections import defaultdict
import random
import math

def assign_groups(n, ngroups, classificationfile):
    acceptable_classes = ["Coding, ZNF", "Coding, Non-ZNF", "Noncoding, ZNF", "Noncoding, Non-ZNF", "Other"]
    classes = defaultdict(list)
    for line in open(classificationfile):
        line = line.strip().split("\t")
        pnum = int(line[0]) - 1
        pclass = line[1]
        if pclass not in acceptable_classes: pclass = "Other"
        classes[pclass].append(pnum)
    groups = []
    for i in range(ngroups): groups.append([])
    for c in classes.keys():
        lis = classes[c]
        random.shuffle(lis)
        i = 0
        for case in classes[c]:
            print str(case) + "\t" + c
            groups[i].append(case)
            i += 1
            if i >= ngroups: i = 0
    return groups

def extract_data(datafile):
    feature_table = {}
    for line in open(datafile):
        line = line.strip().split("\t")
        feature = line[0]
        feature_table[feature] = line[1:]
    return feature_table

def combine_tables(table1, table2):
    returnTable = {}
    for feature in table1.keys(): returnTable[feature] = table1[feature] + table2[feature]
    return returnTable

def assign_weight(freq):
    if freq >= 0.5 and freq < 0.75: return 1
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

def calculate_score(feature_table, feature_to_weight, case):
    score = 0
    for feature in feature_table.keys():
        if feature_table[feature][case] == "yes": score += feature_to_weight[feature]
        if feature_table[feature][case] == "no": score -= feature_to_weight[feature]
    return score

def test(feature_table, groups, testg, feature_to_weight):
    scores = []
    for case in groups[testg]:
        scores.append(calculate_score(feature_table, feature_to_weight, case))
    return scores

def main(notefile, litfile, classificationfile, ngroups=2):
    random.seed(12345)
    note_table = extract_data(notefile)
    lit_table = extract_data(litfile)
    feature_table = combine_tables(note_table, lit_table)
    n = len(feature_table[feature_table.keys()[0]])
    groups = assign_groups(n, ngroups, classificationfile)
    for testg in range(ngroups):
        feature_to_weight = train(feature_table, groups, testg)
        results = test(feature_table, groups, testg, feature_to_weight)
        for i in range(len(groups[testg])):
            print "\t".join([str(testg + 1), str(groups[testg][i] + 1), str(results[i])])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

