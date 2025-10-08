import csv

# Create a safe int() if values are missing
def safe_int(value, default=0):
    try:
        return int(value) if value else default
    except ValueError:
        return default
    
#create a safe float() if values are missing
def safe_float(value, default=0):
    try:
        return float(value) if value else default
    except ValueError:
        return default

with open("network_incidents.csv", encoding="utf8") as f:
    network_incidents_raw = list(csv.DictReader(f))



network_incidents = [{
    "ticket_id": incident["ticket_id"],
    "week_number": safe_int(incident["week_number"]),
    "site": incident["site"],
    "device_hostname": incident["device_hostname"],
    "severity": incident["severity"],
    "category": incident["category"],
    "description": incident["description"],
    "reported_by": incident["reported_by"],
    "resolution_minutes": safe_int(incident["resolution_minutes"]),
    "affected_users": safe_int(incident["affected_users"]),
    "cost_sek": safe_float(incident["cost_sek"].replace(' ','').replace(',','.')),
    "impact_score": safe_float(incident["impact_score"]),
    "resolution_notes": incident["resolution_notes"]
    
} for incident in network_incidents_raw]

# Create variables to store values
unique_weeks = set()
total_incidents_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
incidents_with_high_users = ""

# Read out data on incidents
for incident in network_incidents:
    
    # List devices with severity "critical"
    if incident.get("severity") == "critical":
        total_incidents_by_severity["critical"] += +1

    # List devices with severity "high"
    if incident.get("severity") == "high":
        total_incidents_by_severity["high"] += +1

    # List devices with severity "medium"
    if incident.get("severity") == "medium":
        total_incidents_by_severity["medium"] += +1

    # List devices with severity "low"
    if incident.get("severity") == "low":
        total_incidents_by_severity["low"] += +1

    # List all incidents that impacted more than 100 users
    if incident["affected_users"] < 100:
        incidents_with_high_users += ("  " + incident["ticket_id"] + "  " + incident["severity"].ljust(16)  + incident["description"] + "\n")




with open('incident_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("Incidentanalys TechCorp AB för vecka:" + "\n")
    f.write("="*50 + "\n\n")
    f.write("Antal incidenter per alvarighetsgrad:\n")
    f.write("-"*30 + "\n")
    f.write("  Critical:".ljust(20) + str(total_incidents_by_severity["critical"]).rjust(3) + "\n")
    f.write("  High:".ljust(20) + str(total_incidents_by_severity["high"]).rjust(3) + "\n")
    f.write("  Medium:".ljust(20) + str(total_incidents_by_severity["medium"]).rjust(3) + "\n")
    f.write("  low:".ljust(20) + str(total_incidents_by_severity["low"]).rjust(3) + "\n\n")
    f.write("Incidenter som påverkat mer än 100 användare:\n")
    f.write("-"*30 + "\n")
    f.write("  Ticket id".ljust(17) + "Alvarighetsgrad".ljust(16) + "Beskrivning\n")
    f.write(incidents_with_high_users + "\n\n")