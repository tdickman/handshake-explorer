FROM        python:3.5

RUN         curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN         apt update && apt install -y nodejs libunbound-dev && rm -rf /var/lib/apt/lists/*

WORKDIR     /app
RUN         pip install pipenv
ADD         Pipfile* /tmp/
RUN         cd /tmp && pipenv install --skip-lock --system --deploy

ADD			hsdexplorer/hsdbin/package.json /app/hsdbin/
RUN			cd hsdbin && npm install

ADD         ./hsdexplorer/ /app/
RUN	    	COLLECTSTATIC=1 python manage.py collectstatic; unset COLLECTSTATIC

ENTRYPOINT  ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level", "debug", "hsdexplorer.wsgi"]
