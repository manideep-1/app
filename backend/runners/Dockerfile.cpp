# C++ runner - no host dependency
FROM gcc:latest

RUN useradd -m -u 10000 -s /bin/sh runner
WORKDIR /workspace

RUN g++ --version

COPY run_cpp.sh /run_cpp.sh
RUN chmod +x /run_cpp.sh && chown runner:runner /run_cpp.sh

USER runner
ENTRYPOINT ["/run_cpp.sh"]
