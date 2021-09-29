# Get Security Appliance Firewalled Services status from Meraki dashboard

The script collects the status of the Meraki MX firewalled services status from the Meraki Dashboard and prints a report.

## Installation

python -m pip install merakifirewalledservices


## Usage

Provide API Key and Organization ID from CLI:

```
merakiFirewalledServices --apikey <myApiKey> --orgid <myOrgId>
```

Or from env vars:

```
export APIKEY=<myApiKey>
export ORGID=<myOrgId>
```

If OrgId is not provided the script prints the list of accessible organization with the provides API Key.
