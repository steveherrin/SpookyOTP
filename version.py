import os
import re
import subprocess


def get_version():
    if os.path.exists('PKG-INFO'):
        return _get_version_from_pkg_info()
    elif os.path.exists('.git'):
        return _get_version_from_git()
    else:
        raise RuntimeError("No PKG-INFO or .git available "
                           "to determine version.")


def _get_version_from_pkg_info():
    """
    Get the version string from PKG-INFO
    """
    with open("PKG-INFO", 'r') as f:
        match = re.search(r"^Version:\s(\S+)$", f.read(), re.MULTILINE)
        try:
            return match.group(1)
        except AttributeError:
            raise RuntimeError("No version string found in PKG-INFO")


def _get_version_from_git():
    """
    Use the git tag to get a PEP compliant version string
    """
    tag = _get_most_recent_git_tag()
    print(tag)
    # e.g. 1.0.1-4-f0f0333
    m = re.match(
        r"(?P<version>\d+\.\d+\.\d+)(?:-(?P<nadd>\d+)-(?P<hash>.+))?",
        tag)
    if not m:
        raise RuntimeError("Git tag doesn't match expected format.")
    version = m.group('version')
    if m.group('nadd') or _is_git_repo_dirty():
        version += ".dev{}+{}".format(m.group('nadd') or '0',
                                      m.group('hash') or _get_git_hash())
    return version


def _is_git_repo_dirty():
    """
    Return true if there are any untracked, unstaged, or uncommitted files
    """
    status = subprocess.check_output(["git", "status", "--porcelain"])
    if status:
        return True
    else:
        return False


def _get_most_recent_git_tag():
    cmd = ["git", "describe", "--tags"]
    tag = subprocess.check_output(cmd, universal_newlines=True).strip()
    return tag


def _get_git_hash():
    cmd = ["git", "rev-parse", "HEAD"]
    hash = subprocess.check_output(cmd, universal_newlines=True).strip()
    return hash[:7]
