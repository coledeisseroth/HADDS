import sys
import os
from collections import defaultdict

def parse_lms(lms_file):
    returnMap = defaultdict(lambda: {"Height":{"male":{},"female":{}}, "Weight":{"male":{},"female":{}}, "OFC":{"male":{},"female":{}}})
    for line in open(lms_file):
        lineData = line.strip("\n").split("\t")
        if lineData[0] == "": continue
        if "Minimum" in lineData[0]: continue
        age = int(lineData[1])
        returnMap[age]["Height"]["male"] = (float(lineData[2]),float(lineData[3]),float(lineData[4]))
        returnMap[age]["Height"]["female"] = (float(lineData[5]),float(lineData[6]),float(lineData[7]))
        returnMap[age]["Weight"]["male"] = (float(lineData[8]),float(lineData[9]),float(lineData[10]))
        returnMap[age]["Weight"]["female"] = (float(lineData[11]),float(lineData[12]),float(lineData[13]))
        returnMap[age]["OFC"]["male"] = (float(lineData[14]),float(lineData[15]),float(lineData[16]))
        returnMap[age]["OFC"]["female"] = (float(lineData[17]),float(lineData[18]),float(lineData[19]))
    return returnMap

def parse_premature_parameters(premature_file):
    returnMap = defaultdict(dict)
    for line in open(premature_file):
        lineData = line.strip().split("\t")
        gestational_age = lineData[0].strip()
        try: gestational_age = int(gestational_age)
        except: continue
        returnMap[gestational_age]["Height"] = (float(lineData[14].strip()), float(lineData[15].strip()))
        returnMap[gestational_age]["Weight"] = (float(lineData[2].strip()) / 1000, float(lineData[3].strip()) / 1000)
        returnMap[gestational_age]["OFC"] = (float(lineData[8].strip()), float(lineData[9].strip()))
    return returnMap


def zscore(value, l, m, s):
    return (((value / m) ** l) - 1) / (l * s)

def extract_age(agestring):
    try: return int(agestring)
    except: pass
    if agestring == "n/a": return "n/a"
    elif "yr" in agestring and "mo" in agestring: return (12 * int(agestring.split(" yr")[0])) + int(agestring.split(" yr ")[1].split(" mo")[0])
    elif "yr" in agestring: return (12 * int(agestring.split(" yr")[0]))
    else: return int(agestring.split(" mo")[0])

def extract_zscore(gestational_age, age, gender, measurementstring, measurement_type, lmsmap):
    try: gestational_age = int(float(gestational_age))
    except: gestational_age = 38
    if measurementstring == "n/a": return "n/a"
    if "%" in measurementstring: return "n/a"
    if age == "n/a" or age == "": return "n/a"
    if "(" in measurementstring:
        age = extract_age(measurementstring.split("(")[1].split(")")[0])
        measurementstring = measurementstring.split(" (")[0]
    else: age = extract_age(age)
    if gestational_age < 38: age -= (38 - gestational_age) / 4
    if age < 0: age = 0
    measurement = float(measurementstring.strip().strip("kg").strip("cm").strip(" ").strip())
    if age not in lmsmap.keys():
        ages = lmsmap.keys()
        ages.sort()
        age = ages[-1]
    l, m, s = lmsmap[age][measurement_type][gender]
    return zscore(measurement, l, m, s)

def extract_birth_zscore(gestational_age, gender, measurementstring, measurement_type, lmsmap, premie_map):
    if measurementstring == "n/a": return "n/a"
    if "%" in measurementstring: return "n/a"
    if gestational_age == "n/a" or gestational_age == "": return "n/a"
    if gestational_age == "term": return extract_zscore(38, 0, gender, measurementstring, measurement_type, lmsmap)
    try: gestational_age = int(float(gestational_age))
    except: return "n/a"
    if "(" in measurementstring:
        gestational_age += extract_age(measurementstring.split("(")[1].split(")")[0]) * 4
        measurementstring = measurementstring.split(" (")[0]
    if gestational_age >= 38: return extract_zscore(38, 0, gender, measurementstring, measurement_type, lmsmap)
    if gestational_age not in premie_map.keys(): return "n/a"
    measurement = float(measurementstring.strip().strip("kg").strip("cm").strip(" ").strip())
    mean, stdev = premie_map[gestational_age][measurement_type]
    return (measurement - mean) / stdev


def compute_zscores(patientfile, lmsmap, premie_map):
    for line in open(patientfile):
        lineData = line.strip().split("\t")
        if lineData[0] == "GENERAL": continue
        patientID = lineData[0]
        gender = lineData[1].strip()
        gestational_age = lineData[9].strip()
        heightzscore = extract_zscore(gestational_age, lineData[4], gender, lineData[3], "Height", lmsmap)
        weightzscore = extract_zscore(gestational_age, lineData[6], gender, lineData[5], "Weight", lmsmap)
        ofczscore = extract_zscore(gestational_age, lineData[8], gender, lineData[7], "OFC", lmsmap)
        birthheightzscore = extract_birth_zscore(gestational_age, gender, lineData[10], "Height", lmsmap, premie_map)
        birthweightzscore = extract_birth_zscore(gestational_age, gender, lineData[11], "Weight", lmsmap, premie_map)
        birthofczscore = extract_birth_zscore(gestational_age, gender, lineData[12], "OFC", lmsmap, premie_map)
        print "\t".join([patientID, str(heightzscore), str(weightzscore), str(ofczscore), str(birthheightzscore), str(birthweightzscore), str(birthofczscore)])


if __name__ == "__main__":
    lms_file = sys.argv[1]
    patientfile = sys.argv[2]
    premature_parameters = sys.argv[3]
    lmsmap = parse_lms(lms_file)
    premie_map = parse_premature_parameters(premature_parameters)
    compute_zscores(patientfile, lmsmap, premie_map)

