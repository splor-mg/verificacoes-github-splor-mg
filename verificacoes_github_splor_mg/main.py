import os
import requests
from github import Github
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_organization_repositories(org_name):
    """Fetch all repositories in the given organization."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")

    g = Github(token)
    org = g.get_organization(org_name)
    return org.get_repos()

def get_project_by_number(org, project_number):
    """Fetch a new GitHub Project by its number using GraphQL."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($org: String!, $number: Int!) {
      organization(login: $org) {
        projectV2(number: $number) {
          id
          title
        }
      }
    }
    """
    variables = {"org": org.login, "number": project_number}
    response = requests.post(
        "https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers
    )
    if response.status_code != 200:
        raise Exception(f"GraphQL query failed with status {response.status_code}: {response.text}")
    response_json = response.json()
    if "errors" in response_json:
        raise Exception(f"GraphQL query returned errors: {response_json['errors']}")
    data = response_json.get("data", {}).get("organization", {}).get("projectV2")
    if not data:
        raise ValueError(f"Project with number {project_number} not found or inaccessible.")
    return data

def link_issue_to_project(issue, project):
    """Link an issue to a new GitHub Project using GraphQL."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    variables = {"projectId": project["id"], "contentId": issue.raw_data["node_id"]}
    response = requests.post(
        "https://api.github.com/graphql", json={"query": mutation, "variables": variables}, headers=headers
    )
    response_json = response.json()
    if response.status_code != 200 or "errors" in response_json:
        print(f"Failed to link issue #{issue.number} to project: {response_json}")
    else:
        print(f"Successfully linked issue #{issue.number} to project.")
        return True
    return False

def is_issue_linked_to_project(issue, project):
    """Check if an issue is already linked to a project using GraphQL."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    has_next_page = True
    end_cursor = None
    all_items = []

    while has_next_page:
        query = """
        query($projectId: ID!, $cursor: String) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100, after: $cursor) {
                nodes {
                  content {
                    ... on Issue {
                      number
                      repository {
                        name
                      }
                    }
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
          }
        }
        """
        variables = {
            "projectId": project["id"],
            "cursor": end_cursor
        }

        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"GraphQL query failed with status {response.status_code}: {response.text}")

        response_json = response.json()
        if "errors" in response_json:
            raise Exception(f"GraphQL query returned errors: {response_json['errors']}")

        items_data = response_json.get("data", {}).get("node", {}).get("items", {})
        all_items.extend(items_data.get("nodes", []))

        page_info = items_data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor")

    # Debug information
    print(f"\nChecking issue #{issue.number} in {issue.repository.name}")
    print(f"Total items in project: {len(all_items)}")

    # Compare issue number and repository name
    # breakpoint()
    for item in all_items:
        content = item.get("content", {})
        if (content and
            content.get("number") == issue.number and
            content.get("repository", {}).get("name") == issue.repository.name):
            print(f"Found match! Issue #{issue.number} is already in project")
            return True

    print(f"Issue #{issue.number} is not in project")
    return False

def iterate_issues_in_repositories(org_name, project_number):
    """Iterate over all issues in all repositories of the organization."""
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)
    org = g.get_organization(org_name)

    # Fetch the project by project number using GraphQL
    project = get_project_by_number(org, project_number)

    repos = get_organization_repositories(org_name)
    for repo in repos:
        print(f"Checking repository: {repo.name}")
        issues = repo.get_issues(state="open")
        for issue in issues:
            print(f"- Issue #{issue.number}: {issue.title}")
            if is_issue_linked_to_project(issue, project):
                print(f"  Issue #{issue.number} is already linked to the project.")
            else:
                print(f"  Issue #{issue.number} is not linked to the project. Linking now...")
                link_issue_to_project(issue, project)

if __name__ == "__main__":
    ORGANIZATION_NAME = "splor-mg"  # Replace with your organization name
    PROJECT_NUMBER = 13  # Replace with your project number
    iterate_issues_in_repositories(ORGANIZATION_NAME, PROJECT_NUMBER)
