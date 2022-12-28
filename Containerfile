FROM python:3

RUN mkdir -p /app/domainmaster && \
    python3 -m pip install --upgrade pip

COPY . /app/domainmaster

RUN pip install -e /app/domainmaster

EXPOSE 5000

CMD [ "python3", "-m", "domainmaster" ]
