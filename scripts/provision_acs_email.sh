#!/usr/bin/env bash
# Provision Azure Communication Services Email and attach it to Braelo-V1.
# Gmail SMTP from Azure datacenter IPs returns 530 Authentication Required.
set -uo pipefail

APP_NAME="${APP_NAME:-Braelo-V1}"
EMAIL_SERVICE_NAME="${EMAIL_SERVICE_NAME:-braelov1bdaq-email}"
COMM_SERVICE_NAME="${COMM_SERVICE_NAME:-braelov1bdaq-comm}"
DATA_LOCATION="${ACS_DATA_LOCATION:-United States}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

run() {
  echo ">> $*"
  "$@"
}

echo "Looking up App Service ${APP_NAME}"
RG="$(az webapp list --query "[?name=='${APP_NAME}'].resourceGroup | [0]" -o tsv | tr -d '\r')"
if [[ -z "${RG}" || "${RG}" == "null" ]]; then
  fail "Could not find App Service ${APP_NAME} in this subscription."
fi
echo "Resource group: ${RG}"

echo "Email-related app setting names:"
az webapp config appsettings list -n "${APP_NAME}" -g "${RG}" --query "[].name" -o tsv \
  | tr -d '\r' \
  | grep -E '^(EMAIL|ACS_|AZURE_COMMUNICATION|SENDGRID|COMMUNICATION)' \
  || echo "(none matched)"

echo "Registering Microsoft.Communication provider if needed"
az provider register --namespace Microsoft.Communication --wait || true

echo "Installing Azure CLI communication extension"
az extension add --name communication --upgrade \
  || az extension add --name communication \
  || fail "Could not install az communication extension"

create_email_service() {
  if az communication email show -n "${EMAIL_SERVICE_NAME}" -g "${RG}" >/dev/null 2>&1; then
    echo "Email service ${EMAIL_SERVICE_NAME} already exists"
    return 0
  fi
  echo "Creating Email Communication Service ${EMAIL_SERVICE_NAME}"
  if az communication email create \
        --name "${EMAIL_SERVICE_NAME}" \
        --location "Global" \
        --data-location "${DATA_LOCATION}" \
        --resource-group "${RG}"; then
    return 0
  fi
  if [[ "${DATA_LOCATION}" != "UnitedStates" ]]; then
    echo "Retrying email service create with data-location UnitedStates"
    az communication email create \
      --name "${EMAIL_SERVICE_NAME}" \
      --location "Global" \
      --data-location "UnitedStates" \
      --resource-group "${RG}"
  else
    return 1
  fi
}

create_email_service || fail "Could not create Email Communication Service (SP may lack Microsoft.Communication permissions)."

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
    --domain-management AzureManaged \
    || fail "Could not create AzureManagedDomain"
fi

from_domain() {
  az communication email domain show \
    --domain-name AzureManagedDomain \
    --email-service-name "${EMAIL_SERVICE_NAME}" \
    -g "${RG}" -o json 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); p=d.get('properties') or d; print(p.get('fromSenderDomain') or p.get('mailFromSenderDomain') or d.get('fromSenderDomain') or '')"
}

FROM_DOMAIN=""
for _ in $(seq 1 36); do
  FROM_DOMAIN="$(from_domain | tr -d '\r')"
  if [[ -n "${FROM_DOMAIN}" && "${FROM_DOMAIN}" != "null" ]]; then
    break
  fi
  echo "Waiting for managed domain DNS..."
  sleep 10
done
if [[ -z "${FROM_DOMAIN}" || "${FROM_DOMAIN}" == "null" ]]; then
  fail "Managed domain did not become ready."
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
    -g "${RG}" \
    || fail "Could not create DoNotReply sender username"
fi

DOMAIN_ID="$(az communication email domain show \
  --domain-name AzureManagedDomain \
  --email-service-name "${EMAIL_SERVICE_NAME}" \
  -g "${RG}" --query id -o tsv | tr -d '\r')"
[[ -n "${DOMAIN_ID}" && "${DOMAIN_ID}" != "null" ]] || fail "Missing domain resource id"

create_comm_service() {
  if az communication show -n "${COMM_SERVICE_NAME}" -g "${RG}" >/dev/null 2>&1; then
    echo "Communication Service ${COMM_SERVICE_NAME} already exists"
    return 0
  fi
  echo "Creating Communication Service ${COMM_SERVICE_NAME}"
  az communication create \
    --name "${COMM_SERVICE_NAME}" \
    --location "Global" \
    --data-location "${DATA_LOCATION}" \
    --resource-group "${RG}" \
  || az communication create \
    --name "${COMM_SERVICE_NAME}" \
    --location "Global" \
    --data-location "UnitedStates" \
    --resource-group "${RG}"
}

create_comm_service || fail "Could not create Communication Service"

echo "Linking managed domain to ${COMM_SERVICE_NAME}"
az communication update \
  --name "${COMM_SERVICE_NAME}" \
  --resource-group "${RG}" \
  --linked-domains "${DOMAIN_ID}" \
  || fail "Could not link managed domain"

CONN="$(az communication list-key -n "${COMM_SERVICE_NAME}" -g "${RG}" --query primaryConnectionString -o tsv | tr -d '\r')"
if [[ -z "${CONN}" || "${CONN}" == "null" ]]; then
  fail "Could not read ACS connection string."
fi
SENDER="DoNotReply@${FROM_DOMAIN}"
echo "ACS sender: ${SENDER}"

az webapp config appsettings set -n "${APP_NAME}" -g "${RG}" --settings \
  "AZURE_COMMUNICATION_CONNECTION_STRING=${CONN}" \
  "ACS_EMAIL_SENDER=${SENDER}" \
  "DEFAULT_FROM_EMAIL=${SENDER}" \
  >/dev/null \
  || fail "Could not set App Service email settings"

echo "Restarting ${APP_NAME} to pick up email settings"
az webapp restart -n "${APP_NAME}" -g "${RG}" >/dev/null || true

echo "Azure email settings attached to ${APP_NAME}."
exit 0
