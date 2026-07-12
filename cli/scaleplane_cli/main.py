import typer
from rich.console import Console
from rich.table import Table

from scaleplane_cli import api
from scaleplane_cli.config import get_api_url, get_token, set_api_url, set_token

console = Console()
auth_app = typer.Typer(help="Authentication commands")
projects_app = typer.Typer(help="Project management")
prompts_app = typer.Typer(help="Prompt versioning")
config_app = typer.Typer(help="CLI configuration")
app = typer.Typer(help="ScalePlane CLI — enterprise infrastructure for agentic systems")

app.add_typer(auth_app, name="auth")
app.add_typer(projects_app, name="projects")
app.add_typer(prompts_app, name="prompts")
app.add_typer(config_app, name="config")


@config_app.command("set")
def config_set(key: str, value: str) -> None:
    """Set a configuration value (api_url)."""
    if key == "api_url":
        set_api_url(value)
        console.print(f"[green]api_url set to {value}[/green]")
    else:
        console.print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(1)


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    console.print(f"API URL: {get_api_url()}")
    console.print(f"Authenticated: {'yes' if get_token() else 'no'}")


@auth_app.command("login")
def auth_login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    """Login with email and password."""
    import httpx

    url = f"{get_api_url()}/auth/login"
    with httpx.Client() as client:
        response = client.post(url, json={"email": email, "password": password})
    if response.status_code != 200:
        console.print(f"[red]Login failed: {response.text}[/red]")
        raise typer.Exit(1)
    set_token(response.json()["access_token"])
    console.print("[green]Logged in successfully[/green]")


@auth_app.command("whoami")
def auth_whoami() -> None:
    """Show current user."""
    user = api.request("GET", "/users/me")
    console.print(f"Email: {user['email']}")
    if user.get("full_name"):
        console.print(f"Name: {user['full_name']}")


@projects_app.command("list")
def projects_list() -> None:
    """List all projects."""
    projects = api.request("GET", "/projects")
    table = Table(title="Projects")
    table.add_column("Name")
    table.add_column("Slug")
    table.add_column("ID")
    for p in projects:
        table.add_row(p["name"], p["slug"], p["id"])
    console.print(table)


@projects_app.command("create")
def projects_create(
    name: str = typer.Option(..., "--name", "-n"),
    slug: str = typer.Option(..., "--slug", "-s"),
    description: str = typer.Option(None, "--description", "-d"),
) -> None:
    """Create a new project."""
    project = api.request("POST", "/projects", json={"name": name, "slug": slug, "description": description})
    console.print(f"[green]Created project {project['name']} ({project['id']})[/green]")


@prompts_app.command("list")
def prompts_list(project: str = typer.Option(..., "--project", "-p", help="Project ID or slug")) -> None:
    """List prompts in a project."""
    projects = api.request("GET", "/projects")
    project_id = None
    for p in projects:
        if p["id"] == project or p["slug"] == project:
            project_id = p["id"]
            break
    if not project_id:
        console.print(f"[red]Project not found: {project}[/red]")
        raise typer.Exit(1)

    prompts = api.request("GET", f"/projects/{project_id}/prompts")
    table = Table(title="Prompts")
    table.add_column("Name")
    table.add_column("Slug")
    table.add_column("Latest")
    table.add_column("Production")
    for p in prompts:
        table.add_row(
            p["name"],
            p["slug"],
            str(p.get("latest_version_number") or "—"),
            str(p.get("production_tag_version") or "—"),
        )
    console.print(table)


@prompts_app.command("push")
def prompts_push(
    file: typer.FileText = typer.Argument(..., help="Prompt content file"),
    project: str = typer.Option(..., "--project", "-p"),
    name: str = typer.Option(..., "--name", "-n"),
    slug: str = typer.Option(None, "--slug", "-s"),
) -> None:
    """Push prompt content as a new version (creates prompt if needed)."""
    projects = api.request("GET", "/projects")
    project_id = None
    for p in projects:
        if p["id"] == project or p["slug"] == project:
            project_id = p["id"]
            break
    if not project_id:
        console.print(f"[red]Project not found: {project}[/red]")
        raise typer.Exit(1)

    prompt_slug = slug or name.lower().replace(" ", "-")
    content = file.read()
    existing = api.request("GET", f"/projects/{project_id}/prompts")
    prompt_id = None
    for pr in existing:
        if pr["slug"] == prompt_slug:
            prompt_id = pr["id"]
            break

    if prompt_id:
        version = api.request("POST", f"/prompts/{prompt_id}/versions", json={"content": content})
        console.print(f"[green]Created version v{version['version_number']} for {prompt_slug}[/green]")
    else:
        result = api.request(
            "POST",
            f"/projects/{project_id}/prompts",
            json={"name": name, "slug": prompt_slug, "content": content},
        )
        console.print(f"[green]Created prompt {result['slug']} v{result.get('latest_version_number', 1)}[/green]")


@prompts_app.command("history")
def prompts_history(
    name: str = typer.Argument(..., help="Prompt slug"),
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Show version history for a prompt."""
    projects = api.request("GET", "/projects")
    project_id = None
    for p in projects:
        if p["id"] == project or p["slug"] == project:
            project_id = p["id"]
            break
    if not project_id:
        console.print(f"[red]Project not found: {project}[/red]")
        raise typer.Exit(1)

    prompts = api.request("GET", f"/projects/{project_id}/prompts")
    prompt_id = None
    for pr in prompts:
        if pr["slug"] == name:
            prompt_id = pr["id"]
            break
    if not prompt_id:
        console.print(f"[red]Prompt not found: {name}[/red]")
        raise typer.Exit(1)

    versions = api.request("GET", f"/prompts/{prompt_id}/versions")
    table = Table(title=f"History: {name}")
    table.add_column("Version")
    table.add_column("Hash")
    table.add_column("Created")
    for v in versions:
        table.add_row(
            str(v["version_number"]),
            v["content_hash"][:12] + "...",
            v["created_at"][:19],
        )
    console.print(table)


@prompts_app.command("promote")
def prompts_promote(
    name: str = typer.Argument(..., help="Prompt slug"),
    project: str = typer.Option(..., "--project", "-p"),
    tag: str = typer.Option("production", "--tag", "-t"),
    version: int = typer.Option(..., "--version", "-v"),
) -> None:
    """Promote a version to a tag."""
    projects = api.request("GET", "/projects")
    project_id = None
    for p in projects:
        if p["id"] == project or p["slug"] == project:
            project_id = p["id"]
            break
    if not project_id:
        console.print(f"[red]Project not found: {project}[/red]")
        raise typer.Exit(1)

    prompts = api.request("GET", f"/projects/{project_id}/prompts")
    prompt_id = None
    for pr in prompts:
        if pr["slug"] == name:
            prompt_id = pr["id"]
            break
    if not prompt_id:
        console.print(f"[red]Prompt not found: {name}[/red]")
        raise typer.Exit(1)

    result = api.request("PUT", f"/prompts/{prompt_id}/tags/{tag}", params={"version_number": version})
    console.print(f"[green]Promoted {name} to {tag} → v{result['version_number']}[/green]")


@prompts_app.command("resolve")
def prompts_resolve(
    name: str = typer.Argument(..., help="Prompt slug"),
    project: str = typer.Option(..., "--project", "-p"),
    tag: str = typer.Option("production", "--tag", "-t"),
) -> None:
    """Resolve and print tagged prompt content."""
    projects = api.request("GET", "/projects")
    project_id = None
    for p in projects:
        if p["id"] == project or p["slug"] == project:
            project_id = p["id"]
            break
    if not project_id:
        console.print(f"[red]Project not found: {project}[/red]")
        raise typer.Exit(1)

    prompts = api.request("GET", f"/projects/{project_id}/prompts")
    prompt_id = None
    for pr in prompts:
        if pr["slug"] == name:
            prompt_id = pr["id"]
            break
    if not prompt_id:
        console.print(f"[red]Prompt not found: {name}[/red]")
        raise typer.Exit(1)

    result = api.request("GET", f"/prompts/{prompt_id}/resolve", params={"tag": tag})
    console.print(f"# {name} ({tag}) v{result['version_number']}")
    console.print(result["content"])


if __name__ == "__main__":
    app()
