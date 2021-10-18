#!/bin/bash
# adaptation of super_netperf that works with -j/-k

run_netperf() {
	loops=$1
	shift
	for ((i=0; i<loops; i++)); do
		prefix="$(printf "%02d" $i) "
        (netperf -s 2 "$@" | sed -e "s/^/$prefix/") &
	done
	wait
}

if [ -z $1 ]; then
    echo "Usage: $0 <nstreams> <netperf args>"
    exit 1
fi

# cgroup=$(awk -F: '$2 == "cpu,cpuacct" { print $3 }' /proc/self/cgroup)

tstart=$(date +%s%N)
cstart=$(cat /sys/fs/cgroup/cpu/cpuacct.usage)
#cstart=$(cat /sys/fs/cgroup/cpu/$cgroup/cpuacct.usage)
mstart=$(cat /sys/fs/cgroup/memory/memory.usage_in_bytes)

run_netperf "$@" | perl -ln -e 'BEGIN { $sum = 0; } END { print "AGGREGATE_THROUGHPUT=$sum"; } if (/ THROUGHPUT=(\S+)$/) { $sum += $1; } print;'

mstop=$(cat /sys/fs/cgroup/memory/memory.usage_in_bytes)
tstop=$(date +%s%N)
cstop=$(cat /sys/fs/cgroup/cpu/cpuacct.usage)
# cstop=$(cat /sys/fs/cgroup/cpu/$cgroup/cpuacct.usage)
mdiff=$((mstop-mstart))
tdiff=$((tstop-tstart))
tdiff1=$((tdiff/1000000000))
echo "Memory start($mstart), end($mstop), diff($mdiff)"
echo "Time taken is $tdiff1 seconds"
bc -l <<EOF
($cstop - $cstart) / ($tstop - $tstart) * 100
EOF
