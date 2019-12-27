FROM debian
COPY scripts/kernelpatch-node.sh /
RUN chmod u+x kernelpatch-node.sh
CMD ["./kernelpatch-node.sh"]
