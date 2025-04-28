import requests

def check_abuseipdb(ip, api_key):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": api_key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()['data']
        return {
            "abuseConfidenceScore": data['abuseConfidenceScore'],
            "totalReports": data['totalReports'],
            "countryCode": data['countryCode'],
        }
    return {}

def check_alienvault(ip, api_key):
    url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
    headers = {"X-OTX-API-KEY": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "reputation": data.get("reputation", 0),
            "pulse_info": data.get("pulse_info", {}).get("count", 0),
        }
    return {}

def enrich_alerts(alerts, abuseipdb_key, otx_key):
    enriched = []
    for alert in alerts:
        ip = alert["src_ip"]
        abuse_data = check_abuseipdb(ip, abuseipdb_key)
        otx_data = check_alienvault(ip, otx_key)

        alert.update({
            "abuseipdb": abuse_data,
            "alienvault": otx_data
        })
        enriched.append(alert)
    return enriched