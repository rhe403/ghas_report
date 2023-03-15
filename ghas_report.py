#!/usr/bin/env python3

import requests
import csv
import json
from datetime import datetime

# Handle API error responses
def api_error_response(response, org_name):
    data = response.json()
    if response.status_code == 400:
        print(f"Error: GitHub API version \"{headers.get('X-GitHub-Api-Version')}\" not supported, check your API version in the config.json file.")
        exit(1)
    if response.status_code == 401:
        print("Error: Authentication failed. Please check your API key.")
        exit(1)
    elif response.status_code == 503:
        print("Error: GitHub API is currently unavailable. Please try again later.")
        exit(1)
    elif response.status_code == 403:
        return(f"Error: Access to organization {org_name} is forbidden. Please check your API key permissions.")
    elif response.status_code == 404:
        if "message" in data:
           return(f"Error: {data['message']}") 
        else:
            return(f"Error: {org_name} not found.")
    else:
        return(f"Error getting alerts for {org_name}: {response.status_code}")  

# Get Code Scanning alerts and alert count
def get_code_scanning_alerts(api_url, api_key, org_name=None, owner=None, repo_name=None):
    if repo_name:
        url = f"{api_url}/repos/{owner}/{repo_name}/code-scanning/alerts?state=open"
    elif org_name:
        url = f"{api_url}/orgs/{org_name}/code-scanning/alerts?state=open"
   
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        code_scanning_alerts = response.json()
        code_scanning_alert_count = len(code_scanning_alerts)
    else:
        error_msg = api_error_response(response, org_name)
        if error_msg is not None:
            print(error_msg)
            return
                
    return code_scanning_alerts, code_scanning_alert_count

# Get Secret Scanning alerts and alert count
def get_secret_scanning_alerts(api_url, api_key, org_name=None, owner=None, repo_name=None):
    if repo_name:       
        url = f"{api_url}/repos/{owner}/{repo_name}/secret-scanning/alerts?state=open"
    elif org_name:
        url = f"{api_url}/orgs/{org_name}/secret-scanning/alerts?state=open"
  
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        secret_scanning_alerts = response.json()
        secret_scanning_alert_count = len(secret_scanning_alerts)
    else:
        error_msg = api_error_response(response, org_name)
        if error_msg is not None:
            print(error_msg)
            return

    return secret_scanning_alerts, secret_scanning_alert_count

# Get Dependabot alerts and alert count
def get_dependabot_alerts(api_url, api_key, org_name=None, owner=None, repo_name=None):
    if repo_name:
        url = f"{api_url}/repos/{owner}/{repo_name}/dependabot/alerts?state=open"
    elif org_name:
        url = f"{api_url}/orgs/{org_name}/dependabot/alerts?state=open"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        dependabot_alerts = response.json()
        dependabot_alert_count = len(dependabot_alerts)  # get the total number of open Dependabot alerts
    else:
        error_msg = api_error_response(response, org_name)
        if error_msg is not None:
            print(error_msg)
            return

    return dependabot_alerts, dependabot_alert_count

# Write alert count to a CSV file
def write_alert_count_csv(alert_count, project_name):
    now = datetime.now()
    filename = f"{project_name}-alert_count-{now.strftime('%Y%m%d%H%M%S')}.csv"

    # Write the header row
    alert_count.insert(0, ['Organization', "Repository", 'Code Scanning Alerts', 'Secret Scanning Alerts', 'Dependabot Alerts'])

    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for alerts in alert_count:
                writer.writerow(alerts)
            print(f"Successfully wrote alert count for project \"{project_name}\" to file {filename}")
    except IOError:
        print(f"Error writing alert count for project {project_name} to file {filename}")

# Write code scan findings to a CSV file
def write_codeql_alerts_csv(codeql_alerts, project_name):    
    now = datetime.now()
    filename = f"{project_name}-codeql_alerts-{now.strftime('%Y%m%d%H%M%S')}.csv"

    # Write the header row
    codeql_alerts.insert(0, ['Organization', 'Repository', 'Date Created', 'Date Updated', 'Severity', 'Rule ID', 'Description', 'File', 'Category', 'GitHub URL'])

    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for codeql_alert in codeql_alerts:
                writer.writerow(codeql_alert)
            print(f"Successfully wrote code scan findings for project \"{project_name}\" to file {filename}")
    except IOError:
        print("Error: I/O error")
        exit(1)

# Write secret scan findings to a CSV file
def write_secretscan_alerts_csv(secretscan_alerts, project_name):    
    now = datetime.now()
    filename = f"{project_name}-secretscan_alerts-{now.strftime('%Y%m%d%H%M%S')}.csv"

    # Write the header row
    secretscan_alerts.insert(0, ['Organization', 'Repository', 'Date Created', 'Date Updated', 'Secret Type Name', 'Secret Type', 'GitHub URL'])

    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for secretscan_alert in secretscan_alerts:
                writer.writerow(secretscan_alert)
            print(f"Successfully wrote secret scan findings for project \"{project_name}\" to file {filename}")
    except IOError:
        print("Error: I/O error")
        exit(1)

# Write DependaBot scan findings to a CSV file
def write_dependabot_alerts_csv(dependabot_alerts, project_name):    
    now = datetime.now()
    filename = f"{project_name}-dependabot_alerts-{now.strftime('%Y%m%d%H%M%S')}.csv"

    # Write the header row
    dependabot_alerts.insert(0, ['Organization', 'Repository', 'Date Created', 'Date Updated', 'Severity', 'Package Name', 'CVE ID', 'Summary', 'Scope', 'Manifest ID', 'GitHub URL'])

    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for dependabot_alert in dependabot_alerts:
                writer.writerow(dependabot_alert)
            print(f"Successfully wrote Dependabot scan findings for project \"{project_name}\" to file {filename}")
    except IOError:
        print("Error: I/O error")
        exit(1)

# Process alert counts for each organization and repository and add them to a list
def alert_count(api_url, api_key, project_data):
    alert_count = []

    for obj_type in ['organizations', 'repositories']:
        for obj_name in project_data.get(obj_type, []):
            if obj_name is not None:
                try:
                    if obj_type == 'organizations':
                        print(obj_name)
                        # alert_count.append([obj_name, "N/A", get_code_scanning_alerts(api_url, api_key, org_name=obj_name)[1], get_secret_scanning_alerts(api_url, api_key, org_name=obj_name)[1], get_dependabot_alerts(api_url, api_key, org_name=obj_name)[1]])
                    elif obj_type == 'repositories':
                        print(obj_name)
                        alert_count.append(["N/A", obj_name, get_code_scanning_alerts(api_url, api_key, repo_name=obj_name)[1], get_secret_scanning_alerts(api_url, api_key, repo_name=obj_name)[1], get_dependabot_alerts(api_url, api_key, repo_name=obj_name)[1]])
                except Exception as e:
                    print(f"Error getting alert count for {obj_name} - {e}")

    return alert_count

# Process code scan alerts for each organization and repository and add them to a list
def code_scanning_alerts(api_url, api_key, project_data):
    codeql_alerts = []

    for obj_type in ['organizations', 'repositories']:
        for obj_name in project_data.get(obj_type, []):
            if obj_name:
                try:
                    owner = project_data.get('owner') if obj_type == 'repositories' else None
                    alerts = get_code_scanning_alerts(api_url, api_key, owner=owner, org_name=obj_name if obj_type == 'organizations' else None, repo_name=obj_name if obj_type == 'repositories' else None)[0]
                    for alert in alerts:
                        codeql_alerts.append([
                            obj_name if obj_type == 'organizations' else alert.get('organization', {}).get('name', "N/A"),
                            obj_name if obj_type == 'repositories' else alert.get('repository', {}).get('name', "N/A"),
                            datetime.strptime(alert.get('created_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            datetime.strptime(alert.get('updated_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            alert.get('rule', {}).get('security_severity_level', "N/A"),
                            alert.get('rule', {}).get('id', "N/A"),
                            alert.get('most_recent_instance', {}).get('message', {}).get('text', "N/A"),
                            alert.get('most_recent_instance', {}).get('location', {}).get('path', "N/A"),
                            alert.get('most_recent_instance', {}).get('category', "N/A"),
                            alert.get('html_url', "N/A")
                        ])
                except Exception as e:
                    print(f"Error getting alerts for {obj_type[:-1]}: {obj_name} - {e}")
    return codeql_alerts

# Process Secret Scanning alerts for each organization and repository and add them to a list
def secret_scanning_alerts(api_url, api_key, project_data):
    secretscan_alerts = []

    for obj_type in ['organizations', 'repositories']:
        for obj_name in project_data.get(obj_type, []):
            if obj_name:
                try:
                    owner = project_data.get('owner') if obj_type == 'repositories' else None
                    alerts = get_secret_scanning_alerts(api_url, api_key, owner=owner, org_name=obj_name if obj_type == 'organizations' else None, repo_name=obj_name if obj_type == 'repositories' else None)[0]
                    for alert in alerts:
                        secretscan_alerts.append([
                            obj_name if obj_type == 'organizations' else alert.get('organization', {}).get('name', "N/A"),
                            obj_name if obj_type == 'repositories' else alert.get('repository', {}).get('name', "N/A"),
                            alert.get('repository', {}).get('name', "N/A"),
                            datetime.strptime(alert.get('created_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            datetime.strptime(alert.get('updated_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            alert.get('secret_type_display_name', "N/A"),
                            alert.get('secret_type', "N/A"),
                            alert.get('html_url', "N/A")
                        ])
                except Exception as e:
                    print(f"Error getting alerts for {obj_type[:-1]}: {obj_name} - {e}")
    return secretscan_alerts

# Process Dependabot alerts for each organization and repository and add them to a list
def dependabot_scanning_alerts(api_url, api_key, project_data):
    dependabot_alerts = []

    for obj_type in ['organizations', 'repositories']:
        for obj_name in project_data.get(obj_type, []):
            if obj_name:
                try:
                    owner = project_data.get('owner') if obj_type == 'repositories' else None
                    alerts = get_dependabot_alerts(api_url, api_key, owner=owner, org_name=obj_name if obj_type == 'organizations' else None, repo_name=obj_name if obj_type == 'repositories' else None)[0]
                    for alert in alerts:
                        dependabot_alerts.append([
                            obj_name if obj_type == 'organizations' else alert.get('organization', {}).get('name', "N/A"),
                            obj_name if obj_type == 'repositories' else alert.get('repository', {}).get('name', "N/A"),
                            datetime.strptime(alert.get('created_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            datetime.strptime(alert.get('updated_at', "N/A"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                            alert.get('security_advisory', {}).get('severity', "N/A"),
                            alert.get('dependency', {}).get('package', {}).get('name', "N/A"),
                            alert.get('security_advisory', {}).get('cve_id', "N/A"),
                            alert.get('security_advisory', {}).get('summary', "N/A"),
                            alert.get('dependency', {}).get('scope', "N/A"),
                            alert.get('dependency', {}).get('manifest_path', "N/A"),
                            alert.get('html_url', "N/A")
                        ])
                except Exception as e:
                    print(f"Error getting alerts for {obj_type[:-1]}: {obj_name} - {e}")
    return dependabot_alerts

def main():
    # Load configuration from config.json file
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print('Error: config.json file not found')
        exit(1)
    except json.JSONDecodeError:
        print('Error: config.json file is not valid JSON')
        exit(1)

    # Get API URL and API key from config    
    api_url = config.get('connection', {}).get('gh_api_url')
    api_key = config.get('connection', {}).get('gh_api_key')
    api_version = config.get('connection', {}).get('gh_api_version')
    
    # Define headers for API requests to GitHub as global variable
    global headers
    headers = {
        "Authorization": f"token {api_key}",
        "X-GitHub-Api-Version": f"{api_version}"
    }
    
    # Get Alert count for each project and write them to a CSV file
    for project_name, project_data in config.get('projects').items():
        if project_name != "":
            write_alert_count_csv(alert_count(api_url, api_key, project_data), project_name)
    '''
    # Get Code scan findings for each organization and write them to a CSV file
    for project_name, project_data in config.get('projects').items():
        if project_name != "":
            write_codeql_alerts_csv(code_scanning_alerts(api_url, api_key, project_data), project_name)
    
    # Get Secret scan findings for each organization and write them to a CSV file
    for project_name, project_data in config.get('projects').items():
        if project_name != "":
            write_secretscan_alerts_csv(secret_scanning_alerts(api_url, api_key, project_data), project_name)
   
   
    # Get Dependabot scan findings for each organization and write them to a CSV file
    for project_name, project_data in config.get('projects').items():
        if project_name != "":
            write_dependabot_alerts_csv(dependabot_scanning_alerts(api_url, api_key, project_data), project_name)
    '''
            
if __name__ == '__main__':
    main()