FROM amazonlinux
# includes includes python and pip
RUN mkdir /beef
# COPY . /src
COPY ./diagram.png /beef/diagram.png
ADD ./load-test.sh /beef/load-test.sh
ADD ./load-test.py /beef/load-test.py
RUN ls -al /beef/load-test.sh
RUN chmod 755 /beef/load-test.sh
RUN yum install -y aws-cli datetime
RUN yum install -y python3-pip python3 python3-setuptools
RUN pip3 install --user requirements.txt || true
# ENTRYPOINT ["sh", "-c","/beef/load-test.sh"]
ENTRYPOINT ["python","/beef/load-test.py"]
