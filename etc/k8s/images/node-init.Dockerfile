FROM debian
COPY scripts/node-init.sh /
RUN chmod u+x node-init.sh
CMD ["./node-init.sh"]
