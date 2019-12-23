FROM debian
COPY scripts/node_init.sh /
RUN chmod u+x node_init.sh
CMD ["./node_init.sh"]
