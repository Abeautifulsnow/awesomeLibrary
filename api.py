import asyncio
import logging
from typing import List

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Some constant variables.
API_PREFIX = "https://api.github.com/repos/"


class RepoOwner(BaseModel):
    login: str


class Repo(BaseModel):
    name: str
    description: str
    language: str
    owner: RepoOwner
    html_url: str


def getAccessToken():
    with open("./token.txt") as fp:
        token = fp.read()

    return token.strip()


class GetRepoInfo:
    def __init__(self, repo_url: str) -> None:
        if not repo_url.startswith("https://github.com/"):
            raise ValueError(
                f"Repo url must be startedwith https://github.com/, got {repo_url}"
            )

        self.repo_url = repo_url
        self._trim_dot_git_suffix()

        self.api_prefix = API_PREFIX

    def _trim_dot_git_suffix(self):
        """Trim the `.git` suffix."""
        if self.repo_url.endswith(".git"):
            self.repo_url = self.repo_url.split(".git")[0]

    def get_repo_url(self) -> str:
        """Get the repository url string.

        Returns:
            str: The repo url.
        """
        return self.repo_url

    @property
    def get_repo_list(self) -> List[str]:
        """Split the repository string with a slash.

        Returns:
            List[str]: ['https:', '', 'github.com', '<username>', '<repositoryname>']
        """
        repo_list = self.repo_url.split("/")
        return repo_list

    def get_repo_name(self) -> str:
        """Return the repository name.

        Returns:
            str: Return the repository name.
        """
        return self.get_repo_list[-1]

    def get_repo_user(self) -> str:
        """Return the repository owner.

        Returns:
            str: Return the repository owner.
        """
        return self.get_repo_list[-2]

    async def request_api(self) -> Repo:
        access_token = getAccessToken()
        if not access_token:
            raise ValueError("Token not found.")

        repoAPI = f"https://api.github.com/repos/{self.repo_url[19:]}"
        logger.info(f"Request repo url: {repoAPI}")

        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(repoAPI)

            if response.status_code != 200:
                logger.fatal(response)
                exit(1)
            else:
                data = response.json()
                result = Repo(**data)
                return result


if __name__ == "__main__":
    rp = GetRepoInfo("https://github.com/Textualize/rich")
    asyncio.run(rp.request_api())
