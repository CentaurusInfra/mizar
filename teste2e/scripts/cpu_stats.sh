#!/bin/bash +x
cgroup=$(awk -F: '$2 == "cpu,cpuacct" { print $3 }' /proc/self/cgroup)

tstart=$(date +%s%N)
#cstart=$(cat /sys/fs/cgroup/cpu/$cgroup/cpuacct.usage)
cstart=$(cat /sys/fs/cgroup/cpu/cpuacct.usage)
mstart=$(cat /sys/fs/cgroup/memory/memory.usage_in_bytes)

gap="${1}"
sleep $gap
mstop=$(cat /sys/fs/cgroup/memory/memory.usage_in_bytes)
tstop=$(date +%s%N)
#cstop=$(cat /sys/fs/cgroup/cpu/$cgroup/cpuacct.usage)
cstop=$(cat /sys/fs/cgroup/cpu/cpuacct.usage)
echo "cgroup = $cgroup"
#echo "cstop = $cstop"
#echo "cstart = $cstart"
#echo "tstop = $tstop"
#echo "tstart = $tstart"
mdiff=$((mstop-mstart))
tdiff=$((tstop-tstart))
tdiff1=$((tdiff/1000000000))
echo "Memory start($mstart), end($mstop), diff($mdiff)"
echo "Time taken is $tdiff1 seconds"
bc -l <<EOF
($cstop - $cstart) / ($tstop - $tstart) * 100
EOF
