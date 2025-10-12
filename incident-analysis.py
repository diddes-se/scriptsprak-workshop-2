import csv
from collections import defaultdict
from collections import Counter

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

# Create swedish format
def format_sek(amount):
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")       

with open("network_incidents.csv", encoding="utf8") as f:
    network_incidents_raw = list(csv.DictReader(f))


# format the input from the .csv file
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
total_incidents_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
incidents_with_high_users = ""
incidents_and_cost = ""
incidents_with_highest_cost_formated = ""
resolution_time_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
stats = defaultdict(lambda: {"total_incidents": 0, "critical":0, "high": 0, "medium": 0, "low": 0, "total_cost": 0.0, "total_minutes": 0})
category_stats = defaultdict(lambda: {"count": 0, "total_impact": 0.0})
avg_impact_per_category = ""
overveiw_by_site = ""
incident_with_the_highest_cost_formated = ""

# add all week numbers to a set
unique_weeks = sorted({incident["week_number"] for incident in network_incidents})

# Read out data on incidents
for incident in network_incidents:

    # List devices with severity "critical"
    if incident.get("severity") == "critical":
        # Count incidents with severity "critical"
        total_incidents_by_severity["critical"] += +1
        # Add time to total resolution time for "critical"
        resolution_time_by_severity["critical"] += incident["resolution_minutes"]

    # List devices with severity "high"
    if incident.get("severity") == "high":
        # Count incidents with severity "high"
        total_incidents_by_severity["high"] += +1
        # Add time to total resolution time for "high"
        resolution_time_by_severity["high"] += incident["resolution_minutes"]

    # List devices with severity "medium"
    if incident.get("severity") == "medium":
        # Count incidents with severity "medium"
        total_incidents_by_severity["medium"] += +1
        # Add time to total resolution time for "medium"
        resolution_time_by_severity["medium"] += incident["resolution_minutes"]

    # List devices with severity "low"
    if incident.get("severity") == "low":
        # Count incidents with severity "low"
        total_incidents_by_severity["low"] += +1
        # Add time to total resolution time for "low"
        resolution_time_by_severity["low"] += incident["resolution_minutes"]

    # List all incidents that impacted more than 100 users
    if incident["affected_users"] > 100:
        incidents_with_high_users += ("  " + incident["ticket_id"] + "  " + incident["severity"].ljust(16)  + incident["description"] + "\n")

    # Collect stats per site
    stats[incident["site"]]["total_incidents"] += 1
    stats[incident["site"]]["total_cost"] += incident["cost_sek"]
    stats[incident["site"]]["total_minutes"] += incident["resolution_minutes"]
    if incident["severity"] in stats[incident["site"]]:
        stats[incident["site"]][incident["severity"]] += 1

    # Collect impact score per category
    category_stats[incident["category"]]["count"] += 1
    category_stats[incident["category"]]["total_impact"] += incident["impact_score"]

# Calculate the total cost of all incidents
total_cost_of_incidents = sum(incident["cost_sek"] for incident in network_incidents)

# Get the five most costly incidents
incidents_with_highest_cost = sorted(network_incidents, key=lambda x: x["cost_sek"], reverse=True)[:5]

# Get the most costly incident
incident_with_the_highest_cost = sorted(network_incidents, key=lambda x: x["cost_sek"], reverse=True)[:1]

# Sum the total number of incidents
total_incidents = sum(total_incidents_by_severity.values())

# Count incidents per device
device_counts = Counter(incident["device_hostname"] for incident in network_incidents)

# Find the device with most incidents
most_common_device, incident_count = device_counts.most_common(1)[0]

# sort out and format highest cost to report
for incident in incidents_with_highest_cost:
    incidents_with_highest_cost_formated += ("  " + incident["ticket_id"].ljust(17)
                                            + incident["site"].ljust(20)
                                            + str(format_sek(incident["cost_sek"])).rjust(9) + " kr  "
                                            + incident["description"]  + "\n"
                                            )

# Format the highest cost incident
for incident in incident_with_the_highest_cost:
    incident_with_the_highest_cost_formated += (incident["ticket_id"] + " "
                                            + "(" + str(format_sek(incident["cost_sek"])) + " kr) "
                                            + incident["device_hostname"] + ", " 
                                            + incident["description"]
                                            )

# Format and add to overveiw_by_site to print in report
for site, data in stats.items():
    avg_minutes = data["total_minutes"] / data["total_incidents"] if data["total_incidents"] else 0
    overveiw_by_site += "  " + site.ljust(20) + str(data["total_incidents"]).rjust(6) + format_sek(data["total_cost"]).rjust(14) +" Kr" + str(round(avg_minutes)).rjust(24) + " min \n"

# Format and save average impact svore per category
for category, data in category_stats.items():
    avg_impact = data["total_impact"] / data["count"] if data["count"] else 0
    avg_impact_per_category += "  " + category.ljust(15) + str(data["count"]).rjust(5) + str(round(avg_impact, 1)).rjust(14) + "\n"

# Export to incidents_by_site.csv
output_file = "incidents_by_site.csv"
with open(output_file, "w", newline="", encoding="utf8") as f:
    writer = csv.writer(f)
    writer.writerow(["site", "total_incident", "critical", "high", "medium", "low", "total_cost_sek", "average_resolution_minutes"])
    for site, data in stats.items():
        avg_minutes = data["total_minutes"] / data["total_incidents"] if data["total_incidents"] else 0
        writer.writerow([site, data["total_incidents"], data["critical"], data["high"], data["medium"], data["low"], format_sek(data['total_cost']), round(avg_minutes)])

# Export to incidents_analysis.txt
with open('incident_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("Incidentanalys TechCorp AB för vecka: " + str(unique_weeks).strip("[]") + "\n")
    f.write("="*50 + "\n\n")
    f.write(f"Totalt antal incidenter: {str(total_incidents)} \n")
    f.write(f"Total kostnad: {format_sek(total_cost_of_incidents)} Kr \n\n")
    f.write("Executive summary \n")
    f.write("-"*50 + "\n")
    f.write(f"Kostnad: Dyraste incidenten: {incident_with_the_highest_cost_formated} \n" )
    f.write(f"Kritisk: Enheten med flest incidenter: {most_common_device} ({incident_count} incidenter) \n\n")
    f.write("Antal incidenter per alvarighetsgrad:\n")
    f.write("-"*50 + "\n")
    f.write("  Critical:".ljust(20) + str(total_incidents_by_severity["critical"]).rjust(3) + "\n")
    f.write("  High:".ljust(20) + str(total_incidents_by_severity["high"]).rjust(3) + "\n")
    f.write("  Medium:".ljust(20) + str(total_incidents_by_severity["medium"]).rjust(3) + "\n")
    f.write("  low:".ljust(20) + str(total_incidents_by_severity["low"]).rjust(3) + "\n\n")
    f.write("Incidenter som påverkat mer än 100 användare:\n")
    f.write("-"*50 + "\n")
    f.write("  Ticket id".ljust(17) + "Alvarighetsgrad".ljust(16) + "Beskrivning \n")
    f.write(incidents_with_high_users + "\n\n")
    f.write("De fem dyraste incidenterna: \n")
    f.write("-"*50 + "\n")
    f.write("  Ticket id".ljust(19) + "Site".ljust(20) + "Kostnad".ljust(14) + "Beskrivning \n")
    f.write(incidents_with_highest_cost_formated + "\n")
    f.write("Översikt per site: \n")
    f.write("-"*50 + "\n")
    f.write("  Site".ljust(18) + "Incidenter".ljust(12) + "Totalkostnad".ljust(18) + "Genomsnittlig lösningstid \n" )
    f.write(overveiw_by_site + "\n") 
    f.write("Genomsnittlig lösningstid per alvarlighetsgrad: \n")
    f.write("-"*50 + "\n")
    f.write("  Critical:".ljust(15) + str(round(resolution_time_by_severity["critical"] / total_incidents_by_severity["critical"])) + " min \n")
    f.write("  High:".ljust(15) + str(round(resolution_time_by_severity["high"] / total_incidents_by_severity["high"])) + " min \n")
    f.write("  Medium:".ljust(15) + str(round(resolution_time_by_severity["medium"] / total_incidents_by_severity["medium"])) + " min \n")
    f.write("  Low:".ljust(15) + str(round(resolution_time_by_severity["low"] / total_incidents_by_severity["low"])) + " min \n\n")
    f.write("Genomsnittlig impact score per kategori: \n")
    f.write("-"*50 + "\n")
    f.write("  Kategori".ljust(17) + "Antal".ljust(10) + "Genomsnit \n" )   
    f.write(avg_impact_per_category)
    