FROM debian
COPY scripts/kernelupdate-node.sh /
COPY scripts/node-init.sh /
COPY scripts/transitd-start.sh /
COPY scripts/load-transit-xdp.sh /
RUN chmod u+x kernelupdate-node.sh node-init.sh transitd-start.sh load-transit-xdp.sh
