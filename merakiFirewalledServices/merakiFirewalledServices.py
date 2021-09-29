import os
import click
import meraki
import logging
import sys
from rich import print
from rich.console import Console
from rich.table import Table
import rich
from rich.progress import track


def _validate_apikey(ctx, apikey, value):
    """
    Validate API Key.
    """
    try:
        click.echo("Validating API Key")
        m = meraki.DashboardAPI(
            api_key=value, print_console=False, output_log=False, suppress_logging=True
        )
        m.organizations.getOrganizations()
        ctx.obj = {"apikey": value}
        click.echo("API Key is valid")
        return value
    except:
        raise click.BadParameter("Provided API Key can't access the Meraki Dashboard")


def _validate_orgid(ctx, orgid, value):
    """
    Validate Organization ID.
    Prints a list of accessible Organization if Org ID is missing or invalid.
    """
    try:
        click.echo(f"Validating Organization ID {value}")
        apikey = ctx.obj.get("apikey")
        m = meraki.DashboardAPI(
            api_key=apikey, print_console=False, output_log=False, suppress_logging=True
        )
        networks = m.organizations.getOrganizationNetworks(value, total_pages="all")
        return value
    except:
        m = meraki.DashboardAPI(
            api_key=apikey, print_console=False, output_log=False, suppress_logging=True
        )
        orgs = m.organizations.getOrganizations()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ORGANIZATION ID")
        table.add_column("ORGANIZATION NAME")
        for org in orgs:
            table.add_row(
                org.get("id"),
                org.get("name"),
            )
        console = Console()
        console.print(table)
        raise click.BadParameter(f"Provide a valid Organization ID\n")


@click.command(
    "--help,",
    help="""Get Meraki MX Firewall Appliance Services configuration - ICMP, SNMP, web (Local Status Page).""",
)
@click.option(
    "--apikey",
    required=True,
    is_eager=True,
    prompt="Meraki Dashboard API Key",
    help="API Key",
    envvar="APIKEY",
    callback=_validate_apikey,
)
@click.option(
    "--orgid",
    # required=True,
    prompt="Organization ID",
    help="Organization ID",
    envvar="ORGID",
    callback=_validate_orgid,
)
@click.pass_context
def main(ctx, apikey: str, orgid: str):
    m = meraki.DashboardAPI(
        api_key=apikey, print_console=False, output_log=False, suppress_logging=True
    )
    networks = m.organizations.getOrganizationNetworks(orgid, total_pages="all")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("NETWORK NAME")
    table.add_column("ICMP")
    table.add_column("ICMP ALLOWED")
    table.add_column("SNMP ACCESS")
    table.add_column("SNMP ALLOWED")
    table.add_column("WEB ACCESS")
    table.add_column("WEB ALLOWED")

    default = "unsupported"  # default value for missing services
    sep = ","  # separator for alloweIps list

    for net in track(
        sorted(networks, key=lambda i: i["name"]), description="Processing networks..."
    ):
        if "appliance" in net.get("productTypes"):
            netId = net.get("id")
            netName = net.get("name")
            services = m.appliance.getNetworkApplianceFirewallFirewalledServices(netId)

            i = [s for s in services if s.get("service", "") == "ICMP"]
            icmp = i[0].get("access") if i else default
            icmpAllowed = sep.join(i[0].get("allowedIps", "")) if i else ""

            s = [s for s in services if s.get("service", "") == "SNMP"]
            snmp = s[0].get("access") if s else default
            snmpAllowed = sep.join(s[0].get("allowedIps", "")) if s else ""

            w = [s for s in services if s.get("service", "") == "web"]
            web = w[0].get("access") if w else default
            webAllowed = sep.join(w[0].get("allowedIps", "")) if w else ""

            table.add_row(
                netName, icmp, icmpAllowed, snmp, snmpAllowed, web, webAllowed
            )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()