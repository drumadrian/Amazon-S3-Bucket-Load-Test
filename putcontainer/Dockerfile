FROM amazonlinux
# includes includes python and pip
RUN mkdir /app
# COPY . /src
COPY ./diagram.png /app/diagram.png
ADD ./load-test.sh /app/load-test.sh
RUN ls -al /app/load-test.sh
RUN chmod 755 /app/load-test.sh
RUN yum install -y aws-cli datetime
RUN yum install -y wget unzip
RUN yum install -y python3-pip python3 python3-setuptools
COPY requirements.txt /
RUN pip3 install --user -r requirements.txt
ADD ./load-test.py /app/load-test.py
# ENTRYPOINT ["sh", "-c","/app/load-test.sh"]
# ENTRYPOINT ["python3","/app/load-test.py"]








ARG DT_API_URL="https://xsq45105.live.dynatrace.com/api"
ARG DT_API_TOKEN="GDtJBRnKTjSaGM3EmsiIs"
ARG DT_ONEAGENT_OPTIONS="flavor=default&include=all"
ENV DT_HOME="/opt/dynatrace/oneagent"
RUN mkdir -p "$DT_HOME" && \
    wget -O "$DT_HOME/oneagent.zip" "$DT_API_URL/v1/deployment/installer/agent/unix/paas/latest?Api-Token=$DT_API_TOKEN&$DT_ONEAGENT_OPTIONS" && \
    unzip -d "$DT_HOME" "$DT_HOME/oneagent.zip" && \
    rm "$DT_HOME/oneagent.zip"
ENTRYPOINT [ "/opt/dynatrace/oneagent/dynatrace-agent64.sh" ]
# CMD [ "executable", "param1", "param2" ] # the command of your application, for example, Java
CMD [ "python3", "/app/load-test.py" ] # the command of the application




