from rich.console import Console
from rich.table import Table

def display_cve_table(cve_items):
    console = Console()

    if not cve_items:
        console.print("[bold red]No CVEs matched the given filter.[/bold red]")
        return
    
    severity_color = {
        "LOW" : "green",
        "MEDIUM" : "yellow",
        "HIGH" : "red",
        "CRITICAL" : "bold red"
    }
    table = Table(title=f"FIltered CVEs ({len(cve_items)})",show_lines=True)

    table.add_column("ID",style="cyan",no_wrap=True)
    table.add_column("Severity",style="red")
    table.add_column("Score",style="magenta")
    table.add_column("Description",style="white",overflow="fold")

    for cve in cve_items:
        severity = cve.get("severity","N/A")
        colored_severity = f"[{severity_color.get(severity,'white')}]{severity}[/{severity_color.get(severity,'white')}]"

        table.add_row(
            cve["id"],
            colored_severity,
            str(cve.get("score","N/A")),
            cve["description"][:150] + ("..." if len(cve["description"])>150 else "")
        )
    console.print(table)


