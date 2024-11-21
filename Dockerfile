FROM python:3.12-slim as pybuilder

# Set the working directory
WORKDIR /app

# Install necessary build tools and libraries
RUN apt update && apt install -y python3-dev build-essential wget

# Download and build TA-Lib from source
RUN cd /tmp && \
    wget https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xf ta-lib-0.4.0-src.tar.gz && cd ta-lib && \
    wget -O config.guess https://git.savannah.gnu.org/cgit/config.git/plain/config.guess && \
    wget -O config.sub https://git.savannah.gnu.org/cgit/config.git/plain/config.sub && \
    ./configure --prefix=/usr && \
    make && make install \
    && cd && rm -rf /tmp/ta-lib

# Install PDM
RUN pip3 install pdm==2.20.1 && pdm config python.use_venv false 

# Copy project files
COPY pyproject.toml pdm.lock ./

# Configure PDM and install dependencies
RUN pdm install
