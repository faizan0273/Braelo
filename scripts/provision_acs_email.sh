#!/usr/bin/env bash
# Provision Azure Communication Services Email and attach it to Braelo-V1.
# Gmail SMTP from Azure datacenter IPs returns 530 Authentication Required.
set -euo pipefail

APP_NAME="${APP_NAME:-Braelo-V1}"
EMAIL_SERVICE_NAME="${EMAIL_SERVICE_NAME:-braelov1bdaq-email}"
COMM_SERVICE_NAME="${COMM_SERVICE_NAME:-braelov1bdaq-comm}"
DATA_LOCATION="${ACS_DATA_LOCATION:-United States}"

echo "Looking up App Service ${APP_NAME}"
RG="$(az webapp list --query "[?name=='${APP_NAME}'].resourceGroup | [0]" -o tsv)"
if [[ -z "${RG}" || "${RG}" == "null" ]]; then
  echo "Could not find App Service ${APP_NAME} in this subscription." >&2
  exit 1
fi
echo "Resource group: ${RG}"

echo "Email-related app settings (name + length only):"
az webapp config appsettings list -n "${APP_NAME}" -g "${RG}" \
  --query "[?starts_with(name, 'EMAIL') || starts_with(name, 'ACS_') || starts_with(name, 'AZURE_COMMUNICATION') || starts_with(name, 'SENDGRID')].{name:name, chars:length(value)}" \
  -o table

az extension add --name communication --upgrade --yes >/dev/null

if ! az communication email show -n "${EMAIL_SERVICE_NAME}" -g "${RG}" >/dev/null 2>&1; then
  echo "Creating Email Communication Service ${EMAIL_SERVICE_NAME}"
  az communication email create \
    --name "${EMAIL_SERVICE_NAME}" \
    --location "Global" \
    --data-location "${DATA_LOCATION}" \
    --resource-group "${RG}" >/dev/null
fi

if ! az communication email domain show \
      --domain-name AzureManagedDomain \
      --email-service-name "${EMAIL_SERVICE_NAME}" \
      -g "${RG}" >/dev/null 2>&1; then
  echo "Creating Azure managed email domain"
  az communication email domain create \
    --domain-name AzureManagedDomain \
    --email-service-name "${EMAIL_SERVICE_NAME}" \
    --location "Global" \
    --resource-group "${RG}" \
    --domain-management AzureManaged >/dev/null
fi

FROM_DOMAIN=""
for _ in $(seq 1 36); do
  FROM_DOMAIN="$(az communication email domain show \
    --domain-name AzureManagedDomain \
    --email-service-name "${EMAIL_SERVICE_NAME}" \
    -g "${RG}" \
    --query "[fromSenderDomain, properties.fromSenderDomain, mailFromSenderDomain, properties.mailFromSenderDomain] | [?@ && @ != 'null'] | [0]" -o tsv 2>/dev/null || true)
  if [[ -n "${FROM_DOMAIN}" && "${FROM_DOMAIN}" != "null" ]]; then
    break
  fi
  echo "Waiting for managed domain DNS..."
  sleep 10
done
if [[ -z "${FROM_DOMAIN}" || "${FROM_DOMAIN}" == "null" ]]; then
  echo "Managed domain did not become ready." >&2
  exit 1
fi
echo "Managed domain: ${FROM_DOMAIN}"

if ! az communication email domain sender-username show \
      --domain-name AzureManagedDomain \
      --email-service-name "${EMAIL_SERVICE_NAME}" \
      --sender-username DoNotReply \
      -g "${RG}" >/dev/null 2>&1; then
  echo "Creating DoNotReply sender username"
  az communication email domain sender-username create \
    --domain-name AzureManagedDomain \
    --email-service-name "${EMAIL_SERVICE_NAME}" \
    --sender-username DoNotReply \
    --username DoNotReply \
    --display-name Braelo \
    -g "${RG}" >/dev/null
fi

DOMAIN_ID="$(az communication email domain show \
  --domain-name AzureManagedDomain \
  --email-service-name "${EMAIL_SERVICE_NAME}" \
  -g "${RG}" --query id -o tsv)"

if ! az communication show -n "${COMM_SERVICE_NAME}" -g "${RG}" >/dev/null 2>&1; then
  echo "Creating Communication Service ${COMM_SERVICE_NAME}"
  az communication create \
    --name "${COMM_SERVICE_NAME}" \
    --location "Global" \
    --data-location "${DATA_LOCATION}" \
    --resource-group "${RG}" \
    --linked-domains "${DOMAIN_ID}" >/dev/null
else
  echo "Linking managed domain to ${COMM_SERVICE_NAME}"
  az communication update \
    --name "${COMM_SERVICE_NAME}" \
    --resource-group "${RG}" \
    --linked-domains "${DOMAIN_ID}" >/dev/null
fi

CONN="$(az communication list-key -n "${COMM_SERVICE_NAME}" -g "${RG}" --query primaryConnectionString -o tsv)"
if [[ -z "${CONN}" || "${CONN}" == "null" ]]; then
  echo "Could not read ACS connection string." >&2
  exit 1
fi
SENDER="DoNotReply@${FROM_DOMAIN}"
echo "ACS sender: ${SENDER}"

az webapp config appsettings set -n "${APP_NAME}" -g "${RG}" --settings \
  "AZURE_COMMUNICATION_CONNECTION_STRING=${CONN}" \
  "ACS_EMAIL_SENDER=${SENDER}" \
  "DEFAULT_FROM_EMAIL=${SENDER}" \
  >/dev/null

echo "Azure email settings attached to ${APP_NAME}."
