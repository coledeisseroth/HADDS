from ctypes.wintypes import FLOAT
from distutils.log import error
from itertools import filterfalse
from pickle import FALSE, TRUE
import sys
import os
from collections import defaultdict
import random
import math
from tkinter import NONE
from tokenize import group
from unicodedata import numeric
import openpyxl
import pandas as pd




"""Assign study cases into two random groups both used to train the program 
Feature_df: Dataframe, should be rawdata.txt as dataframe 
ngroups: Int, number of groups to use for crossvalidation, default 2 
Returns two groups one, one to be used as a test group and another to set weighted feature scores"""
def assign_groups(feature_df, ngroups):
    groups = list()
    for i in range(ngroups):
        name = 'group{}'.format(i+1)
        if len(groups) == 0:
            groups.append(feature_df.sample(frac = 1/ngroups, axis =1, random_state = 1))
        else:
            new_df = feature_df
            for df in groups:
                new_df = new_df.drop(df, axis = 1)        
            groups.append(new_df)  
    return groups

"""Converts txt files to Dataframe
data: csv, should be all data files to be tested 
Returns data file as Dataframe"""
def extract_data(data):
    feature_df = pd.read_csv(data, sep = "\t", index_col = 0, header = 1)
    return feature_df


"""Assigns feature weights based on frequency 
Freq: Int, frequency of study patients with selected feature 
Returns feature weight"""
def assign_weight(freq):
    if freq == 1: return 1
    if freq > 0.75: return 0.75
    if freq > 0.5: return 0.5
    if freq > 0.25: return 0.25
    return 0


"""Trains algorithm to assign weighted feature scores based on half of the study data frame 
Feature_df: Dataframe, should be rawdata.txt as dataframe 
Groups: List, list of feature_df randomly divided into two separate dataframes
Test: Int, defines which group will be used for testing 
Returns feature_to_weight dictionary"""
def train(feature_df, groups, test):
    feature_to_weight = {}
    for feature in feature_df.index:
        n = 0
        pos = 0
        for i in range(len(groups)):
            group = groups[i]
            if i == test: continue
            for case in group.columns:
                n += 1
                if feature_df.loc[feature, case] == "yes": pos += 1
        freq = float(pos) / float(n)  
        feature_to_weight[feature] = assign_weight(freq)
        feature_to_weight_df = pd.DataFrame.from_dict(feature_to_weight, orient = 'index', columns = ['Feature Weight'])
        feature_to_weight_df.to_excel(writer, sheet_name =('Feature to Weight Trial -' + str(test+1)))
    return feature_to_weight

"""Calculates maximum possible score 
feature_to_weight: Dictionary, feature keys with corresponding frequency weights 
Returns Int Returnscore which is the maximum score given that all features are present"""
def max_score(feature_to_weight):
    returnScore = 0
    for feature in feature_to_weight.keys():
            if is75PercentGlobal:   
                if feature_to_weight[feature] >= 0.75:  
                    returnScore += feature_to_weight[feature] 
            else:
                returnScore += feature_to_weight[feature] 
    return returnScore

"""Calculates individual score for each patient 
feature_df: Dataframe, dataframe of data to be tested  
feature_to_weight: Dictionary, feature keys with corresponding frequency weights 
case: Patient ID or Proband # 
Returns Int Score (for our study EBF3 DBS Score)"""
def calculate_score(feature_df, feature_to_weight, case):
    score = 0
    for feature in feature_df.index:    
        if feature_df.loc[feature, case] == "yes": 
            if is75PercentGlobal:   
                if feature_to_weight[feature] >= 0.75:   
                    score += feature_to_weight[feature]
            else:
                score += feature_to_weight[feature]
    return math.ceil(score * 10 / max_score(feature_to_weight))

"""Tests algorithm - assigns scores to all patients in test group for study data, nonHADDS data, and literature data 
feature_df: Dataframe, dataframe of data to be tested  
groups: List, list of dataframes 
testg: Int, defines which group is the test group 
feature_to_weight: Dictionary, feature keys with corresponding frequency weights 
Returns scores_df a Dataframe with patient ID, Score, Trial, and Gender""" 
def test(feature_df, groups, testg, feature_to_weight):
    scores = {}
    for case in groups[testg].columns:
        scores[case] = [(calculate_score(feature_df, feature_to_weight, case)), (testg +1), (groups[testg]).loc['Gender',case]]
    scores_df = pd.DataFrame.from_dict(scores, orient = 'index', columns = ['EBF3 DBS Score', 'Trial', 'Gender'])
    return scores_df

"""Runs algorithm - trains and tests algorithm twice using both halves of the study data to crossvalidate scores 
feature_df: Dataframe, dataframe of data to be tested  
rawdata: Txt, file with study data
nonHADDS_data: Txt, file with nonHADDS data
lit_data: Txt, file with literature data
ngroups: Int, number of groups to divide rawdata into for crossvalidation, default 2
is75Percent: Bool, whether or not you want to test all Features or just the features present in 75% or > of cases 
Returns excel file with sheets for Feature_to_Weight scores, Study DBS Scores, NonHADDS DBS Scores, and Literature DBS Scores for each Trial""" 
def main(rawdata, nonHADDS_data, lit_data, is75Percent = False):
    global is75PercentGlobal
    is75PercentGlobal = is75Percent
    global writer
    if is75PercentGlobal:
        writer = pd.ExcelWriter(r'C:\Users\u239249\Documents\HADDS_Scoring_75Percent.xlsx')
    else:
        writer = pd.ExcelWriter(r'C:\Users\u239249\Documents\HADDS_Scoring.xlsx')
    ngroups = 2
    feature_df = extract_data(rawdata)
    nonHADDS_df = extract_data(nonHADDS_data)
    lit_df = extract_data(lit_data)
    nonHADDS_group = list()
    lit_group = list()
    nonHADDS_group.append(nonHADDS_df)
    lit_group.append(lit_df)
    groups = assign_groups(feature_df, ngroups)
    for testg in range(ngroups):
        feature_to_weight = train(feature_df, groups, testg)
        test(feature_df, groups, testg, feature_to_weight).to_excel(writer, sheet_name = ('Study DBS Score Trial -' + str(testg +1)))
        test(nonHADDS_df, nonHADDS_group, 0, feature_to_weight).to_excel(writer, sheet_name = ('NonHADDS DBS Score Trial -' + str(testg +1)))
        test(lit_df, lit_group, 0, feature_to_weight).to_excel(writer, sheet_name = ('Literature DBS Score Trial -' + str(testg +1)))
    writer.save()     


"""
sys.argv[1]: Txt, rawdata.txt
sys.argv[2]: Txt, nonHADDS.txt
sys.argv[3]: Txt, litdata.txt
sys.argv[4]: Bool, whether or not you want to test all Features (FALSE) or just the features present in 75% or > of cases (TRUE)
"""
if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])