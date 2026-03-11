# C runner - no host dependency
FROM gcc:latest

RUN useradd -m -u 10000 -s /bin/sh runner
WORKDIR /workspace

RUN gcc --version

COPY run_c.sh /run_c.sh
RUN chmod +x /run_c.sh && chown runner:runner /run_c.sh

USER runner
ENTRYPOINT ["/run_c.sh"]
