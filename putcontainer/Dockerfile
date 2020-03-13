FROM amazonlinux
# includes includes python and pip
RUN mkdir /app
# COPY . /src
COPY ./diagram.png /app/diagram.png
ADD ./load-test.sh /app/load-test.sh
RUN ls -al /app/load-test.sh
RUN chmod 755 /app/load-test.sh
RUN yum install -y aws-cli datetime
RUN yum install -y python3-pip python3 python3-setuptools
COPY requirements.txt /
RUN pip3 install --user -r requirements.txt
ADD ./load-test.py /app/load-test.py
# ENTRYPOINT ["sh", "-c","/app/load-test.sh"]
ENTRYPOINT ["python3","/app/load-test.py"]
