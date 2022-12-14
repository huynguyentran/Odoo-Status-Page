FROM 811770454613.dkr.ecr.us-east-1.amazonaws.com/base-image:odoo15.novobi.com-2022-08-14

#Install requirements
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY ./entrypoint.sh /
COPY ./make_env.py /

RUN chmod +x /entrypoint.sh && chmod +x /opt/odoo/odoo/odoo-bin
RUN apt-get update && apt install -y geoip-database


ADD . /opt/odoo/customized_addons/

VOLUME ["/var/lib/odoo"]

EXPOSE 8069

ENTRYPOINT ["/entrypoint.sh"]
