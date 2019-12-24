FROM debian
COPY scripts/load_transit_xdp.sh /
RUN chmod u+x load_transit_xdp.sh
CMD ["./load_transit_xdp.sh"]
