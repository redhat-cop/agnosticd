#!/bin/bash
ORIG="$(cd "$(dirname "$0")" || exit; pwd)"

output_dir=/tmp/stats_agnosticd
mkdir -p $output_dir

FY19_start=2018-03-01
FY19_end=2019-03-01
FY20_start=2019-03-01
FY20_end=2020-03-01

FY19_first_commit=$(git log --no-color --after=${FY19_start} --oneline | tail -n 1 |awk '{print $1}')
FY19_last_commit=$(git log --no-color --before=${FY19_end} --oneline | head -n 1| awk '{print $1}')
FY20_first_commit=$(git log --no-color --after=${FY20_start} --oneline | tail -n 1 |awk '{print $1}')
FY20_last_commit=$(git log --no-color --before=${FY20_end} --oneline | head -n 1| awk '{print $1}')

cd ${ORIG}/../ansible/roles

FY19_start_workloads=$(git ls-tree -d --name-only ${FY19_first_commit} | grep -E 'ocp4?-workload' | wc -l)
FY19_end_workloads=$(git ls-tree -d --name-only ${FY19_last_commit} | grep -E 'ocp4?-workload' | wc -l)
FY20_start_workloads=$(git ls-tree -d --name-only ${FY20_first_commit} | grep -E 'ocp4?-workload' | wc -l)
FY20_end_workloads=$(git ls-tree -d --name-only ${FY20_last_commit} | grep -E 'ocp4?-workload' | wc -l)
total_workloads_today=$(git ls-tree -d --name-only HEAD | grep -E 'ocp4?-workload'|wc -l)

echo "########################"
echo "Workloads"
echo "  total before FY19: ${FY19_start_workloads}"
echo "  total today: ${total_workloads_today}"
echo "  created in FY19: $((FY19_end_workloads - FY19_start_workloads + 1))"
echo "  created in FY20: $((FY20_end_workloads - FY20_start_workloads + 1))"

echo
echo
echo "  new workloads since FY19 started: new_workloads_fy19.txt"
echo "  new workloads in FY20: new_workloads_fy20.txt"
git ls-tree --name-only ${FY19_first_commit} | grep -E 'ocp4?-workload' > ${output_dir}/before_workloads.txt
git ls-tree --name-only ${FY19_last_commit} | grep -E 'ocp4?-workload' |grep -vf ${output_dir}/before_workloads.txt > ${output_dir}/new_workloads_fy19.txt
git ls-tree --name-only HEAD| grep -E 'ocp4?-workload' |grep -vf ${output_dir}/before_workloads.txt |grep -vf ${output_dir}/new_workloads_fy19.txt > ${output_dir}/new_workloads_fy20.txt

cd ${ORIG}/../ansible/configs

FY19_start_configs=$(git ls-tree -d --name-only ${FY19_first_commit} | wc -l)
FY19_end_configs=$(git ls-tree -d --name-only ${FY19_last_commit} | wc -l)
FY20_start_configs=$(git ls-tree -d --name-only ${FY20_first_commit} | wc -l)
FY20_end_configs=$(git ls-tree -d --name-only ${FY20_last_commit} | wc -l)
total_configs_today=$(git ls-tree -d HEAD| wc -l)

echo
echo "########################"
echo "Configs (not accurate since we renamed and moved some to archive)"
echo "  total before FY19: ${FY19_start_configs}"
echo "  total today: ${total_configs_today}"
echo "  created in FY19: $((FY19_end_configs - FY19_start_configs + 1))"
echo "  created in FY20: $((FY20_end_configs - FY20_start_configs + 1))"

echo
echo
echo "  new configs since FY19 started: new_configs_fy19.txt"
echo "  new configs in FY20: new_configs_fy20.txt"

git ls-tree -d --name-only ${FY19_first_commit} > ${output_dir}/before_configs.txt
git ls-tree -d --name-only ${FY19_last_commit} |grep -vf ${output_dir}/before_configs.txt > ${output_dir}/new_configs_fy19.txt
git ls-tree -d HEAD |grep -vf ${output_dir}/before_configs.txt |grep -vf ${output_dir}/new_configs_fy19.txt > ${output_dir}/new_configs_fy20.txt
cp new_configs*txt ${output_dir}/


echo
echo "########################"
echo "Contributors"
git shortlog -s -n $FY19_first_commit | awk '{print $2,$3,$4}' > ${output_dir}/contributors_before_fy19.txt
git shortlog -s -n $FY20_first_commit | awk '{print $2,$3,$4}' > ${output_dir}/contributors_before_fy20.txt
git shortlog -s -n $FY19_first_commit..$FY19_last_commit | awk '{print $2,$3,$4}' |grep -vf ${output_dir}/contributors_before_fy19.txt> ${output_dir}/new_contributors_fy19.txt
git shortlog -s -n $FY20_first_commit..$FY20_last_commit | awk '{print $2,$3,$4}' |grep -vf ${output_dir}/contributors_before_fy20.txt> ${output_dir}/new_contributors_fy20.txt

echo "Total contributors: $(git shortlog -s -n |wc -l)"
echo "FY19 new contributors: $(cat ${output_dir}/new_contributors_fy19.txt|wc -l)"
echo "FY20 new contributors: $(cat ${output_dir}/new_contributors_fy20.txt|wc -l)"
echo
echo "(new_contributors_fy19.txt)"
echo "(new_contributors_fy20.txt)"
