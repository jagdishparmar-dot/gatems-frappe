FROM frappe/bench:latest

USER frappe
WORKDIR /home/frappe
RUN bench init frappe-bench --skip-redis-config-generation

WORKDIR /home/frappe/frappe-bench
COPY pyproject.toml README.md license.txt ./apps/gatems/
COPY gatems ./apps/gatems/gatems
RUN ./env/bin/pip install -e ./apps/gatems \
	&& mkdir -p sites \
	&& (grep -qx gatems sites/apps.txt || echo gatems >> sites/apps.txt)

USER root
RUN apt-get update \
	&& apt-get install -y --no-install-recommends nginx gettext-base curl \
	&& rm -rf /var/lib/apt/lists/* \
	&& mkdir -p /etc/nginx/snippets \
	&& printf '%s\n' \
		'add_header X-Frame-Options "SAMEORIGIN";' \
		'add_header X-Content-Type-Options "nosniff";' \
		> /etc/nginx/snippets/security_headers.conf

COPY docker/nginx/nginx-template.conf /etc/nginx/templates/frappe.conf.template
COPY docker/nginx/nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
RUN chmod +x /usr/local/bin/nginx-entrypoint.sh \
	&& rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

COPY docker/configure.sh docker/create-site.sh /opt/
RUN chmod +x /opt/configure.sh /opt/create-site.sh

USER frappe
WORKDIR /home/frappe/frappe-bench
