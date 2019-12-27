FROM debian
COPY scripts/load-transit-xdp.sh /
RUN chmod u+x load-transit-xdp.sh
CMD ["./load-transit-xdp.sh"]
