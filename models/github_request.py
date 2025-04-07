from pydantic import BaseModel

class GitHubRequest(BaseModel):
    github_url: str
    instructions : str