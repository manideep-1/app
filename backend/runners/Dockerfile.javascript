# Node.js runner - no host dependency
FROM node:20-slim

RUN useradd -m -u 10000 -s /bin/sh runner
WORKDIR /workspace

RUN node --version && npm --version

USER runner
CMD ["node", "/workspace/code.js"]
