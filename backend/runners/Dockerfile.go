# Go runner - no host dependency (Alpine uses adduser, not useradd)
FROM golang:1.22-alpine

RUN adduser -D -u 10000 -s /bin/sh runner
WORKDIR /workspace

RUN go version

USER runner
# Full code (package main + user func + func main) mounted at /workspace/main.go
CMD ["go", "run", "/workspace/main.go"]
