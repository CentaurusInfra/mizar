FROM debian
COPY scripts/kernelpatch-node.sh /
COPY scripts/node-init.sh /
COPY scripts/transitd-start.sh /
COPY scripts/load-transit-xdp.sh /
RUN chmod u+x kernelpatch-node.sh node-init.sh transitd-start.sh load-transit-xdp.sh
