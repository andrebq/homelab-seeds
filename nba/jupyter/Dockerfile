FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Base venv: pre-installed packages baked into the image.
# A user venv is created at runtime inside the volume (see entrypoint.sh).
RUN uv venv /opt/jupyter-base
ENV VIRTUAL_ENV=/opt/jupyter-base
ENV PATH="/opt/jupyter-base/bin:$PATH"

RUN uv pip install --no-cache \
    jupyterlab \
    ipykernel \
    # core numerics
    numpy \
    pandas \
    polars \
    scipy \
    # ML
    scikit-learn \
    statsmodels \
    # visualization
    matplotlib \
    seaborn \
    plotly \
    altair \
    # I/O formats
    pyarrow \
    openpyxl \
    xlrd \
    # HTTP / misc
    requests \
    httpx \
    tqdm

RUN mkdir -p /var/jupyter-data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/var/jupyter-data"]

EXPOSE 8888

# Set to a non-empty value to require a token, e.g. -e JUPYTER_TOKEN=secret
ENV JUPYTER_TOKEN=""

ENTRYPOINT ["/entrypoint.sh"]
CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--notebook-dir=/var/jupyter-data"]
