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

# Create a function to identify device type from hostname
def detect_device_type(hostname: str) -> str:
    if not hostname:
        return "okänd"
    prefix = hostname[:2].lower()
    mapping = {
        "ap": "Accesspunkt",
        "sw": "Switch",
        "rt": "Router",
        "fw": "Brandvägg",
        "lb": "Lastbalanserare"
    }
    return mapping.get(prefix, "Okänd")      

with open("network_incidents.csv", encoding="utf8") as f:
    network_incidents_raw = list(csv.DictReader(f))


# format the input from the .csv file and add device type
network_incidents = [{
    "ticket_id": incident["ticket_id"],
    "week_number": safe_int(incident["week_number"]),
    "site": incident["site"],
    "device_hostname": incident["device_hostname"],
    "device_type": detect_device_type(incident["device_hostname"]),
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
stats_per_site = defaultdict(lambda: {"total_incidents": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "total_cost": 0.0, "total_minutes": 0})
device_summary = defaultdict(lambda: {"site": None, "category": None, "incident_count": 0, "total_impact_score": 0, "avg_impact_score": 0.0,  "total_cost_sek": 0.0, "total_affected_users": 0, "weeks": set(), "severity_levels": set()})
category_stats = defaultdict(lambda: {"count": 0, "total_impact": 0.0})
avg_impact_per_category = ""
overveiw_by_site = ""
incident_with_the_highest_cost_formated = ""
weekly_stats = defaultdict(lambda: {"total_cost": 0.0, "total_impact": 0.0, "incident_count": 0})
result_recurring_issues_analysis = []
result_recurring_issues_analysis_filtered_formated = ""

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
    stats_per_site[incident["site"]]["total_incidents"] += 1
    stats_per_site[incident["site"]]["total_cost"] += incident["cost_sek"]
    stats_per_site[incident["site"]]["total_minutes"] += incident["resolution_minutes"]
    if incident["severity"] in stats_per_site[incident["site"]]:
        stats_per_site[incident["site"]][incident["severity"]] += 1

    # Collect impact score per category
    category_stats[incident["category"]]["count"] += 1
    category_stats[incident["category"]]["total_impact"] += incident["impact_score"]

    # Add data to device_summary
    device_summary[incident["device_hostname"]]["site"] = incident["site"]
    device_summary[incident["device_hostname"]]["category"] = incident["category"]
    device_summary[incident["device_hostname"]]["device_type"] = incident["device_type"]
    device_summary[incident["device_hostname"]]["incident_count"] += 1
    device_summary[incident["device_hostname"]]["total_cost_sek"] += incident["cost_sek"]
    device_summary[incident["device_hostname"]]["total_affected_users"] += incident["affected_users"]
    device_summary[incident["device_hostname"]]["total_impact_score"] += incident["impact_score"]
    device_summary[incident["device_hostname"]]["weeks"].add(incident["week_number"])
    device_summary[incident["device_hostname"]]["severity_levels"].add(incident["severity"])

    # Add data to weekly_stats
    weekly_stats[incident["week_number"]]["total_cost"] += incident["cost_sek"]
    weekly_stats[incident["week_number"]]["total_impact"] += incident["impact_score"]
    weekly_stats[incident["week_number"]]["incident_count"] += 1


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
for site, data in stats_per_site.items():
    avg_minutes = data["total_minutes"] / data["total_incidents"] if data["total_incidents"] else 0
    overveiw_by_site += "  " + site.ljust(20) + str(data["total_incidents"]).rjust(6) + format_sek(data["total_cost"]).rjust(14) +" Kr" + str(round(avg_minutes)).rjust(24) + " min \n"

# Format and save average impact svore per category
for category, data in category_stats.items():
    avg_impact = data["total_impact"] / data["count"] if data["count"] else 0
    avg_impact_per_category += "  " + category.ljust(15) + str(data["count"]).rjust(5) + str(round(avg_impact, 1)).rjust(14) + "\n"

# Calculate average impact score and users in device_summary
for device, data in device_summary.items():
    if data["incident_count"] > 0:
        data["avg_impact_score"] = round(data["total_impact_score"] / data["incident_count"], 1)
        data["avg_affected_users"] = round(data["total_affected_users"] / data["incident_count"])
    else:
        data["avg_impact_score"] = 0
        data["avg_affected_users"] = 0

# Sort device_summary after highest incident_count and total_cost_sek
sorted_device_summary = sorted(device_summary.items(), key=lambda x: (x[1]["incident_count"], x[1]["total_cost_sek"]), reverse=True)

# Calculate average per week
for week, data in weekly_stats.items():
    data["avg_impact_score"] = round(data["total_impact"] / data["incident_count"], 1) if data["incident_count"] > 0 else 0.0

# Sort weekly_stats to sorted_weekly_stats
sorted_weekly_stats = sorted(weekly_stats.items(), key=lambda x: x[0])

# Identify recurring problems
for device, stats in device_summary.items():
    if stats["incident_count"] == 0:
        continue

    avg_impact = round(stats["total_impact_score"] / stats["incident_count"], 1)
    recurring_weeks = len(stats["weeks"])
    avg_cost = round(stats["total_cost_sek"] / stats["incident_count"], 2)

    # Logic to suggest actions to recurring problems
    if stats["incident_count"] >= 5 or recurring_weeks >= 2 or avg_impact > 7:
        if avg_impact > 8 or "critical" in stats["severity_levels"]:
            action = "Omedelbar granskning av hårdvara / firmware - hög risk!"
        else:
            action = "Undersök mönster i drift / konfiguration."
    else:
        action = "Inga allvarliga återkommande problem."

    result_recurring_issues_analysis.append({
        "hostname": device,
        "incident_count": stats["incident_count"],
        "recurring_weeks": recurring_weeks,
        "avg_impact_score": avg_impact,
        "avg_cost_sek": avg_cost,
        "suggested_action": action
    })

# Filter out devices wit no recurring or critical problems
result_recurring_issues_analysis_filterd = [
    result for result in result_recurring_issues_analysis
    if result["suggested_action"] != "Inga allvarliga återkommande problem."
]


# Sort result_recurring_issues_analysis after incident count, awg impact score and awg cost with highest first
result_recurring_issues_analysis.sort(key=lambda x: (x["incident_count"], x["avg_impact_score"], x["avg_cost_sek"]), reverse=True)

# Format result_recurring_issues_analysis to report
for device in result_recurring_issues_analysis_filterd:
    result_recurring_issues_analysis_filtered_formated += ("  " + device["hostname"].ljust(15)
                                              + str(device["incident_count"]).rjust(13)
                                              + str(device["recurring_weeks"]).rjust(14)
                                              + str(device["avg_impact_score"]).rjust(17)
                                              + format_sek(device["avg_cost_sek"]).rjust(22) + " Kr  "
                                              + device["suggested_action"] + "\n"
                                              )


# Export data to incidents_by_site.csv
output_file = "incidents_by_site.csv"
with open(output_file, "w", newline="", encoding="utf8") as f:
    writer = csv.writer(f)
    writer.writerow(["site", "total_incident", "critical", "high", "medium", "low", "total_cost_sek", "average_resolution_minutes"])
    for site, data in stats_per_site.items():
        avg_minutes = data["total_minutes"] / data["total_incidents"] if data["total_incidents"] else 0
        writer.writerow([site, data["total_incidents"], data["critical"], data["high"], data["medium"], data["low"], format_sek(data['total_cost']), round(avg_minutes)])


# Export data to problem_devices.csv
output_file = "problem_devices.csv"
with open(output_file, "w", newline="", encoding="utf8") as f:
    writer = csv.writer(f)
    writer.writerow(["device_hostname", "site", "device_type", "incident_count", "avg_severity_score", "total_cost_sek", "awg_affected_users"])
    for device, data in sorted_device_summary:
        writer.writerow([device, data["site"], 
                         data["device_type"], 
                         data["incident_count"], 
                         data["avg_impact_score"], 
                         format_sek(data["total_cost_sek"]),                         
                         data["avg_affected_users"], 
                        ])

# Export data to cost_analysis.csv
output_file = "cost_analysis.csv"
with open(output_file, "w", newline="", encoding="utf8") as f:
    writer = csv.writer(f)
    writer.writerow(["week_number", "incident_count", "total_cost_sek", "avg_impact_score"])

    for week, data in sorted_weekly_stats:
        writer.writerow([week, data["incident_count"], format_sek(data['total_cost']), data["avg_impact_score"]])

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
    f.write(avg_impact_per_category + "\n")
    f.write("Föreslagna åtgärder för enheter med återkommande problem: \n")
    f.write("-"*50 + "\n")
    f.write("  Hostname".ljust(20) + "Incidenter".ljust(12) + "Antal veckor".ljust(13) + "Alvarlighetsgrad".ljust(20)+ "Genomsnittlig kostnad" + "  Föreslagen åtgärd" + "\n")
    f.write(result_recurring_issues_analysis_filtered_formated)
    