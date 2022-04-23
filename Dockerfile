FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 9000-9100

ENV SECRET_KEY="lkasmdflkl5k235k51"
ENV EMAIL_ADDRESS="someemail@somewhere.net"
ENV EMAIL_PASS="123445"

CMD [ "python", "./spaceroombas/server.py" ]