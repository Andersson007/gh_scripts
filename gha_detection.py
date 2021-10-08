#!/usr/bin/python3

# 1. Get a list of the collections to check
# 2. Clone them all do a directory
# 3. In a loop, run
# cat repo.list | while read LINE; do echo ===== $LINE =====; cd $LINE; \
# ~/ignore_txt/copy_ignore_txt.py \
# -s tests/sanity/ignore-2.11.txt \
# -d tests/sanity/ignore-2.12.txt -b test_1 \
# -u https://github.com/ansible-collections/$LINE.git \
# -m "Copy ignore-2.11.txt to ignore-2.12.txt"; \
# cd ..; done

import os.path
import sys

from argparse import ArgumentParser
from shutil import copyfile
from subprocess import Popen, PIPE


def get_cli_args():
    """Gets, parses, and returns CLI arguments"""
    parser = ArgumentParser(description='Test')

    parser.add_argument('-g', '--grep',
                        dest='grep',
                        metavar='GREP',
                        default=False,
                        required=False,
                        help='Expression to grep')

    parser.add_argument('-s', '--src',
                        dest='src',
                        metavar='SRC',
                        default=False,
                        required=True,
                        help='Source file')

    parser.add_argument('-b', '--branch',
                        dest='branch',
                        metavar='BRANCH',
                        default=False,
                        required=False,
                        help='Name of new branch to checkout and push')

    parser.add_argument('-u', '--upstream',
                        dest='upstream',
                        metavar='UPSTREAM',
                        default=False,
                        required=True,
                        help='URL of upstream repo')

    parser.add_argument('-m', '--msg',
                        dest='msg',
                        metavar='COMMIT_MSG',
                        default=False,
                        required=False,
                        help='Commit message')

    return parser.parse_args()


def run_cli_cmd(command: list):
    # command is a list containing a command to execute
    # plus arguments, for example ['echo', '"Hello World"']
    p = Popen(command, stdout=PIPE, encoding='UTF-8')

    out, err = p.communicate()
    rc = p.returncode

    return out, err, rc


def get_default_branch():
    out, err, rc = run_cli_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    default_branch = out.rstrip('\n')

    if default_branch == 'master':
        print('WARNING: the default branch is "master"')

    return default_branch


def check_upstream():
    out, err, rc = run_cli_cmd(['git', 'remote', '-v'])

    if 'upstream' in out:
        return True

    return False


def add_upstream(upstream):
    if check_upstream():
        print('WARNING: upstream is already exists, skipped')
        return

    out, err, rc = run_cli_cmd(['git', 'remote', 'add', 'upstream', upstream])


def pull_upstream(branch):
    out, err, rc = run_cli_cmd(['git', 'pull', 'upstream', branch])


def checkout_branch(branch):
    out, err, rc = run_cli_cmd(['git', 'checkout', '-b', branch])


def source_file_exists(src):
    return os.path.exists(src)


def git_add(file):
    out, err, rc = run_cli_cmd(['git', 'add', file])


def git_commit(msg):
    out, err, rc = run_cli_cmd(['git', 'commit', '-m', msg])


def git_push_origin(branch):
    out, err, rc = run_cli_cmd(['git', 'push', 'origin', branch])


def grep_expr_recur(directory, expression):
    out, err, rc = run_cli_cmd(['grep', '-r', expression, directory])
    return False if rc else True


def create_changelog_fragment():
    if os.path.exists('changelog/fragments'):
        changelog_dir = 'changelog/fragments'

    elif os.path.exists('changelogs/fragments'):
        changelog_dir = 'changelogs/fragments'

    else:
        return None

    fragment_path = changelog_dir + '/0-copy_ignore_txt.yml'
    if os.path.exists(fragment_path):
        fragment_path = changelog_dir + '/00-copy_ignore_txt.yml'

    with open(fragment_path, 'w') as f:
        f.writelines(['---\n', 'trivial:\n', '  - Copy ignore.txt.\n'])

    return fragment_path


def main():
    # Parse CLI arguments
    args = get_cli_args()

    # Get default branch
    def_branch = get_default_branch()

    # Add upstream
    add_upstream(args.upstream)

    # Update local main branch
    pull_upstream(def_branch)

    # Exit if the source file does not exist
    if not source_file_exists(args.src):
        # print('WARNING: source file %s does not exist, exit\n' % args.src)
        sys.exit(0)

    if grep_expr_recur(args.src, args.grep):
        sys.exit(0)

    print('%s: grep has not found "%s"' % (args.upstream, args.grep))

    # Exit if the source file does not exist
    # if not source_file_exists(args.src):
    #     print('WARNING: source file %s does not exist, exit\n' % args.src)
    #     sys.exit(0)

    # Exit if the destination file exists
    # if source_file_exists(args.dst):
    #     print('WARNING: destination file %s exists, exit\n' % args.dst)
    #     sys.exit(0)

    # Checkout a new branch
    if args.branch:
        checkout_branch(args.branch)

    # Copy the file
    # copyfile(args.src, args.dst)

    # Add the file to git
    # git_add(args.dst)

    # Create changelog fragment
    # fragment_path = create_changelog_fragment()

    # Add changelog
    # if fragment_path:
    #     git_add(fragment_path)

    # Commit the changes
    # git_commit(args.msg)

    # Push the branch to origin
    # git_push_origin(args.branch)

    # print('=== Go and open a PR in %s ===\n' % args.upstream)


if __name__ == '__main__':
    main()
