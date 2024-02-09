#!/bin/sh
# entrypoint.sh
chmod +x /usr/share/nginx/inject-env.sh

# Run your environment variable injection script
sh /usr/share/nginx/inject-env.sh

# Then start Nginx in the foreground
nginx -g 'daemon off;'
