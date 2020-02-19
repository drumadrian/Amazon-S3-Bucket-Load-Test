FROM amazonlinux
# includes includes python and pip
RUN mkdir /beef
# COPY . /src
COPY ./diagram.png /beef/diagram.png
ADD ./load-test.sh /beef/load-test.sh
RUN ls -al /beef/load-test.sh
RUN chmod 755 /beef/load-test.sh
RUN yum install -y aws-cli
ENTRYPOINT ["sh", "-c","/beef/load-test.sh"]
