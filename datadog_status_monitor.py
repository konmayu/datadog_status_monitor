import requests
import feedparser
import re
from dotenv import load_dotenv

# .envをロード
load_dotenv()

WEBHOOK_URL = os.getenv("DATADOG_WEBHOOK_URL")

def send_notification(is_normal_status, service_name=None, incident_status=None, incident_details=None, incident_created=None, incident_updated=None, incident_resolved=None):
    if is_normal_status:
        message = {"text": "Everything is normal with Datadog services."}
    else:
        message = {
            "text": f"Datadog Incident Alert\nService: {service_name}\nStatus: {incident_status}\nDetails: {incident_details}\nCreated: {incident_created}\nUpdated: {incident_updated}\nResolved: {incident_resolved}"
        }
    requests.post(WEBHOOK_URL, json=message)

def main():
    url = "https://status.datadoghq.com/history.rss"
    feed = feedparser.parse(url)

    is_normal_status = True
   # is_normal_status = False

    for entry in feed.entries:
        service_status = entry["title"]
        print(service_status)
       # if service_status == 'major_outage' or service_status == 'partial_outage':
        if re.match(r"major_outage|partial_outage", service_status):
            is_normal_status = False
            service_name = entry["summary"]
            incident_status = entry["dd_status"]
            incident_details = entry["content"][0]["value"]
            incident_created = entry["published"]
            incident_updated = entry["updated"]
            incident_resolved = entry["dd_resolved"]
            send_notification(is_normal_status, service_name, incident_status, incident_details, incident_created, incident_updated, incident_resolved)

    if is_normal_status:
        send_notification(is_normal_status)

if __name__ == "__main__":
    main()

