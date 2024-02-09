#!/bin/sh
# This script generates a JavaScript file that injects runtime environment variables
export $(cat /usr/share/nginx/.env | xargs)

cat <<EOF > /usr/share/nginx/html/env.js
window._env_ = {
  REACT_APP_MSAL_TENANT: "${REACT_APP_MSAL_TENANT}",
  REACT_APP_MSAL_CLIENT: "${REACT_APP_MSAL_CLIENT}",
  REACT_APP_DOMAIN: "${REACT_APP_DOMAIN}",
  REACT_APP_WEBENV: "${REACT_APP_WEBENV}",
  REACT_APP_CLIENT_APP_NAME: "${REACT_APP_CLIENT_APP_NAME}",
  REACT_APP_APP_NAME: "${REACT_APP_APP_NAME}",
  REACT_APP_PORT: "${REACT_APP_PORT}",
}
EOF
