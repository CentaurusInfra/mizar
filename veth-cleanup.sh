sudo ip l delete $(ip l | grep -Po "(br-\w+)(?=:)")
for name in $(ip l |  grep -Po '(veth-\w+)(?=@)'); do sudo ip l delete $name; done
sudo ip -all netns delete

