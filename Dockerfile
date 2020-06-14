FROM python:3

ADD aries_basic_controller aries_basic_controller
ADD requirements.txt .
ADD setup.py .
ADD README.md .
ADD demo/example.py .


RUN pip3 install --no-cache-dir -e .





CMD [ "python", "./example.py" ]