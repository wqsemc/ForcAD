FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev

ADD backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD docker_config/await_start.sh /await_start.sh
ADD docker_config/db_check.py /db_check.py
ADD docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

########## CUSTOMIZE ##########

# uncomment blocks to enable features
### pwntools dependencies ###
################
#RUN apt-get install -y git libssl-dev libffi-dev build-essential
#ENV PWNLIB_NOTERM=true
################

### selenium (chromedriver) dependencies (from https://github.com/joyzoursky/docker-python-chromedriver) ###
################
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable
#RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
################

ADD ./checkers/requirements.txt /checker_requirements.txt
RUN pip install -r /checker_requirements.txt

ADD ./checkers /checkers

########## END CUSTOMIZE ##########

ADD backend /app

ADD ./docker_config/celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER nobody

CMD ["/entrypoint.sh"]