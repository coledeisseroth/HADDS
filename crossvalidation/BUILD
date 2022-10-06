#If you copy-paste the current study phenotype excel sheet into raw/rawdata.txt, this should work fine.
cat raw/rawdata.txt | awk 'BEGIN {FS = "\t"} $2 == "yes" || $2 == "no" || $2 == "n/a"' | grep -vw "CNV deletion" > data.txt
#If you copy-paste the non-HADDS phenotype excel sheet into raw/nonHADDS.txt, this should work fine.
cat raw/nonHADDS.txt | awk 'BEGIN {FS = "\t"} $2 == "yes" || $2 == "no" || $2 == "n/a"' | grep -vw "CNV deletion" > nonHADDS_data.txt
#If you copy-paste the literature phenotype sheet into raw/rawdata.txt, this should work fine.
cat raw/litdata.txt | cut -f$(cat raw/litdata.txt | grep "Enrolled in current study" | tail -1 | sed 's/\t/\n/g' | grep -wvn yes | cut -d':' -f1 | paste -sd,) | awk 'BEGIN {FS = "\t"} $2 == "yes" || $2 == "no" || $2 == "n/a"' | grep -vw "CNV deletion" | grep -vw "OFC" | grep -vw "Enrolled" > litdata.txt


(cat raw/rawdata.txt | grep "Variant type 2"; cat raw/litdata.txt | cut -f$(cat raw/litdata.txt | grep "Enrolled in current study" | tail -1 | sed 's/\t/\n/g' | grep -wvn yes | cut -d':' -f1 | paste -sd,) | grep "Variant type 2") | cut -f2- | sed 's/\t/\n/g' | awk '{print NR "\t" $0}' > patient_to_variant_type.txt
(cat raw/rawdata.txt | grep "GENERAL"; cat raw/litdata.txt | cut -f$(cat raw/litdata.txt | grep "Enrolled in current study" | tail -1 | sed 's/\t/\n/g' | grep -wvn yes | cut -d':' -f1 | paste -sd,) | grep "GENERAL") | cut -f2- | sed 's/\t/\n/g' | awk '{print NR "\t" $0}' > patient_to_study_ID.txt


(cat raw/rawdata.txt | grep "Cerebellar anomaly"; cat raw/litdata.txt | cut -f$(cat raw/litdata.txt | grep "Enrolled in current study" | tail -1 | sed 's/\t/\n/g' | grep -wvn yes | cut -d':' -f1 | paste -sd,) | grep "Cerebellar anomaly") | cut -f2- | sed 's/\t/\n/g' | awk '{print NR "\t" $0}' > patient_to_cerebellum.txt

cat raw/DDSS_delays.txt | cut -f1,3- | grep "Average months delayed" | cut -f2- | sed 's/\t/\n/g' | awk '{if($1 == ""){print "n/a"} else{print $0}}' | awk '{print NR "\t" $0}' > average_delays.txt



python src/bootstrap_DDSS.py data.txt litdata.txt patient_to_variant_type.txt | sort -k2,2 | join -t$'\t' -1 2 -2 1 - <(cat patient_to_variant_type.txt | sort -k1,1) | join -t$'\t' - <(cat average_delays.txt | sort -k1,1) | awk 'BEGIN {FS = "\t"} $5 != "n/a"' | awk 'BEGIN {FS = "\t"} {print $0 "\t" ($5 * (1.3 ** $3))}' | join -t$'\t' - <(cat patient_to_cerebellum.txt | sort -k1,1) | sort -k1,1g > DDSS_bootstrap_results.txt


cat patient_to_study_ID.txt | sort -k1,1 | join -t$'\t' - <(cat DDSS_bootstrap_results.txt | sort -k1,1) | sort -k1,1g | cut -f2,3,7 > patient_ID_to_DDSS_score.txt

(python src/bootstrap.py data.txt nonHADDS_data.txt | grep -v TESTEE | grep -v '\[' | sort -k1,1g | awk '{print "Proband "$0}'; python src/bootstrap.py data.txt nonHADDS_data.txt | grep TESTEE | sed 's/TESTEE-1/Trial 1, Proband E/g' | sed 's/TESTEE-2/Trial 2, Proband E/g' | awk 'BEGIN {FS = "\t"}{print $1 "\tn/a\t" $3}' | awk 'BEGIN {FS = "\t"} {print substr($1, index($1, "-") + 1) "\t" $0}' | sort -k1,1g | cut -f2-; python src/bootstrap.py data.txt litdata.txt | grep TESTEE | cut -f1,3 | sed 's/TESTEE-//g' | sed 's/-/\t/g' | sort -k2,2 | join -t$'\t' -1 2 -2 1 - <(cat patient_to_study_ID.txt | grep M- | awk '{print $1 - '$(cat patient_to_study_ID.txt | grep -v M- | wc -l)' "\t" $0}' | cut -f1,3 | sort -k1,1) | awk 'BEGIN {FS = "\t"} {print "Trial " $2 ", " $4 "\tn/a\t" $3}' | awk 'BEGIN {FS = "\t"} {print substr($1, index($1, "-") + 1) "\t" $0}' | sort -k1,1g | cut -f2-)

