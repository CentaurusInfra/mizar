FROM debian
COPY scripts/transitd-start.sh /
RUN chmod u+x transitd-start.sh
CMD ["./transitd-start.sh"]
