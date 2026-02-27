#!/bin/bash

# Cloudflare DDNS Update Script
# Reads config from environment variables or ~/.config/ddns/ddns.env

# ===========================================
# Load config from env file if vars not set
# ===========================================
ENV_FILE="${DDNS_ENV_FILE:-$HOME/.config/ddns/ddns.env}"
if [ -f "$ENV_FILE" ]; then
    # shellcheck source=/dev/null
    source "$ENV_FILE"
fi

# ===========================================
# Required environment variables:
#   CF_API_TOKEN    - Cloudflare API token
#   CF_ZONE_ID      - Cloudflare zone ID
#   CF_RECORD_NAME  - DNS record name (e.g., home.example.com)
# Optional:
#   CF_RECORD_TYPE  - default: A
#   CF_TTL          - default: 300
#   CF_PROXIED      - default: false
# ===========================================

: "${CF_API_TOKEN:?CF_API_TOKEN is required}"
: "${CF_ZONE_ID:?CF_ZONE_ID is required}"
: "${CF_RECORD_NAME:?CF_RECORD_NAME is required}"
CF_RECORD_TYPE="${CF_RECORD_TYPE:-A}"
CF_TTL="${CF_TTL:-300}"
CF_PROXIED="${CF_PROXIED:-false}"

LOG_FILE="${DDNS_LOG_FILE:-$HOME/ddns/ddns.log}"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Get current public IP
CURRENT_IP=$(curl -s https://api.ipify.org)

if [[ ! $CURRENT_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log "ERROR: Failed to get valid public IP"
    exit 1
fi

# Get all DNS records for this name from Cloudflare
RECORD_DATA=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records?type=${CF_RECORD_TYPE}&name=${CF_RECORD_NAME}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json")

RECORD_COUNT=$(echo "$RECORD_DATA" | jq '.result | length')

if [ "$RECORD_COUNT" -eq 0 ]; then
    log "INFO: No DNS record found for ${CF_RECORD_NAME}. Creating..."

    CREATE_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records" \
        -H "Authorization: Bearer ${CF_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data "{\"type\":\"${CF_RECORD_TYPE}\",\"name\":\"${CF_RECORD_NAME}\",\"content\":\"${CURRENT_IP}\",\"ttl\":${CF_TTL},\"proxied\":${CF_PROXIED}}")

    if echo "$CREATE_RESULT" | jq -e '.success' > /dev/null 2>&1; then
        log "SUCCESS: Created DNS record ${CF_RECORD_NAME} -> ${CURRENT_IP}"
    else
        log "ERROR: Failed to create DNS record: $CREATE_RESULT"
        exit 1
    fi
    exit 0
fi

# Delete duplicate records, keeping only the first one
if [ "$RECORD_COUNT" -gt 1 ]; then
    for i in $(seq 1 $((RECORD_COUNT - 1))); do
        DUP_ID=$(echo "$RECORD_DATA" | jq -r ".result[$i].id")
        DUP_IP=$(echo "$RECORD_DATA" | jq -r ".result[$i].content")
        DEL_RESULT=$(curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${DUP_ID}" \
            -H "Authorization: Bearer ${CF_API_TOKEN}" \
            -H "Content-Type: application/json")
        if echo "$DEL_RESULT" | jq -e '.success' > /dev/null 2>&1; then
            log "SUCCESS: Deleted duplicate record ${CF_RECORD_NAME} -> ${DUP_IP} (id: ${DUP_ID})"
        else
            log "ERROR: Failed to delete duplicate record ${DUP_ID}: $DEL_RESULT"
        fi
    done
fi

# Update the first record
RECORD_ID=$(echo "$RECORD_DATA" | jq -r '.result[0].id')
RECORD_IP=$(echo "$RECORD_DATA" | jq -r '.result[0].content')

if [ "$CURRENT_IP" == "$RECORD_IP" ]; then
    log "INFO: IP unchanged (${CURRENT_IP})"
    exit 0
fi

UPDATE_RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${RECORD_ID}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"type\":\"${CF_RECORD_TYPE}\",\"name\":\"${CF_RECORD_NAME}\",\"content\":\"${CURRENT_IP}\",\"ttl\":${CF_TTL},\"proxied\":${CF_PROXIED}}")

if echo "$UPDATE_RESULT" | jq -e '.success' > /dev/null 2>&1; then
    log "SUCCESS: Updated ${CF_RECORD_NAME} from ${RECORD_IP} to ${CURRENT_IP}"
else
    log "ERROR: Failed to update DNS record: $UPDATE_RESULT"
    exit 1
fi
