FROM python:3.12-slim AS pybuilder

WORKDIR /build
RUN apt update && apt install -y python3-dev build-essential wget
RUN cd /tmp && \
    wget https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xf ta-lib-0.4.0-src.tar.gz && cd ta-lib && \
    wget -O config.guess https://git.savannah.gnu.org/cgit/config.git/plain/config.guess && \
    wget -O config.sub https://git.savannah.gnu.org/cgit/config.git/plain/config.sub && \
    ./configure --prefix=/usr && \
    make && make install

COPY pyproject.toml pdm.lock ./
RUN pip3 install pdm==2.20.1 && pdm install


FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=pybuilder /build/.venv/lib/ /usr/local/lib/
COPY --from=pybuilder /usr/lib/libta_lib* /usr/lib/
COPY aicryptobot /app