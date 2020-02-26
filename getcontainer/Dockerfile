FROM amazonlinux
# includes includes python and pip
RUN mkdir /app
ADD ./load-test.py /app/load-test.py
RUN ls -al /app/load-test.py
RUN chmod 755 /app/load-test.py
RUN yum install -y aws-cli datetime
RUN yum install -y python3-pip python3 python3-setuptools
COPY requirements.txt /
RUN pip3 install --user -r requirements.txt
ENTRYPOINT ["python3","/app/load-test.py"]
