from mcp.server import Server
import requests

server = Server("github-demo")

@server.tool()
def list_issues(owner: str, repo: str):
    """
    Connects to the GitHub API and returns open issues (title and body) for the specified repository.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    resp = requests.get(url).json()
    return [{"title": i.get("title"), "body": i.get("body")} for i in resp]

if __name__ == "__main__":
    server.run()