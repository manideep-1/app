# Code execution runtimes

The backend runs user code for **Python**, **JavaScript**, **Java**, **C++**, and **C**. Some runtimes are optional. If a runtime is missing, running code in that language will return a clear error (e.g. "Java is not installed or not available in PATH").

## Required

- **Python** – Uses the same interpreter that runs the server (`sys.executable`). No extra install.

## Optional (install if you want that language)

- **JavaScript** – [Node.js](https://nodejs.org/). Ensure `node` is in your PATH.
- **Java** – A **JDK** (not just JRE) so that both `javac` and `java` are available.
  - Install: [Eclipse Temurin (Adoptium)](https://adoptium.net/) or [OpenJDK](https://openjdk.org/).
  - After installing, ensure `javac` and `java` work in your terminal:
    ```bash
    javac -version
    java -version
    ```
- **C++** – `g++` (e.g. Xcode Command Line Tools on macOS, or `build-essential` on Ubuntu).
- **C** – `gcc` (same as above).

## Check what’s available

- **At startup**: The server logs which runtimes are available and which are missing when it starts.
- **API**: `GET /api/runtimes` returns a JSON object like `{"python": true, "javascript": true, "java": false, "cpp": true, "c": true}`.
