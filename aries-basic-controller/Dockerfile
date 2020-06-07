FROM python:3

ADD . /

RUN pip install aiohttp asyncio prompt_toolkit pygments
EXPOSE 443
CMD [ "python", "./app.py" ]