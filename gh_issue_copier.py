#!/usr/bin/python3
# Copyright: (c) Andrew Klychkov (@Andersson007) <andrew.a.klychkov@gmail.com>
#
# Requirements:
# 1. pip3 install PyGithub
# 2. GitHub access token
#
# Example of how to run it:
# $ ./issue_copier.py -t your_github_token_here [--dry-run] \
# -s <src_org/src_repo> -d <dst_org/$LINE> -i <issue_num>
#
# If you have a list of repos one repo per line,
# to copy an issue to all of them, you can do something like:
# $ cat <repo-list.txt> | while read LINE; do \
# ./issue_copier.py -t your_github_token_here [--dry-run] \
# -s <src_org/src_repo> -d <dst_org/$LINE> -i <issue_num>; done

from argparse import ArgumentParser

from github import (
    Auth,
    Github,
)


def get_cli_args():
    """Get command-line arguments."""
    parser = ArgumentParser(description='.')

    # Access token
    parser.add_argument('-t', '--token',
                        dest='token',
                        required=True,
                        help='GitHub access token',
                        metavar='TOKEN')

    # Source GitHub repo
    parser.add_argument('-s', '--source-repo',
                        dest='source_repo',
                        required=True,
                        help='GitHub org/repo to copy an issue from',
                        metavar='SOURCE')

    # Destination GitHub repo
    parser.add_argument('-d', '--dst-repo',
                        dest='dst_repo', required=True,
                        help='GitHub org/repo to copy an issue to',
                        metavar='DEST')

    # Issue number to copy
    parser.add_argument('-i', '--issue',
                        dest='issue_number',
                        required=True,
                        help='Issue number to copy',
                        metavar='ISSUE_NUM')

    # For debugging
    parser.add_argument('--dry-run', dest='dry_run',
                        action='store_true',
                        required=False,
                        help='Print the new issue, but do NOT create it')

    return parser.parse_args()


def get_repo(g_obj, repo):
    try:
        return g_obj.get_repo(repo)
    except Exception as e:
        print(f"Error occured with {repo}: {e}")
        exit(1)


def main():
    # Get command-line arguments
    cli_args = get_cli_args()

    # Use an access token
    auth = Auth.Token(cli_args.token)

    # Create an instance
    g = Github(auth=auth)

    # Get the src repo
    src_repo = get_repo(g, cli_args.source_repo)
    dst_repo = get_repo(g, cli_args.dst_repo)

    # Get the issue
    i_num = int(cli_args.issue_number)
    src_issue = src_repo.get_issue(number=i_num)

    # Uncomment for debugging if needed
    # Print issue details
    # print(f"Issue #{issue.number}: {issue.title}")
    # print(f"Status: {issue.state}")
    # print(f"Created by: {issue.user.login}")
    # print(f"Body: {issue.body}")

    # Prepare issue data
    title = src_issue.title
    body = (f"Copied from {src_repo.full_name}#"
            f"{src_issue.number}\n\n" + (src_issue.body or ""))

    if not cli_args.dry_run:
        # Create the new issue in the destination repo
        try:
            new_issue = dst_repo.create_issue(
                title=title,
                body=body,
            )
        except Exception as e:
            print(f"Exception occured: {e}")
            exit(1)

        print(f"Issue copied: {new_issue.html_url}")

    print(f"Issue: {title}")
    print(f"Body: {body}")
    g.close()


if __name__ == '__main__':
    main()
