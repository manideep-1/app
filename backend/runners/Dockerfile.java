# Java 17 LTS runner - no host dependency
FROM eclipse-temurin:17-jdk

# UID 10000 to avoid collision with base image users (e.g. temurin uses 1000)
RUN useradd -m -u 10000 -s /bin/sh runner
WORKDIR /workspace

# Verify javac and java are available
RUN javac -version && java -version

COPY run_java.sh /run_java.sh
RUN chmod +x /run_java.sh && chown runner:runner /run_java.sh

USER runner
# Code mounted at /workspace/Main.java; compile then run; stdin = input, stdout = output
ENTRYPOINT ["/run_java.sh"]
