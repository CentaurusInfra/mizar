FROM debian
COPY scripts/transitd_start.sh /
RUN chmod u+x transitd_start.sh
CMD ["./transitd_start.sh"]
