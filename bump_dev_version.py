import os
import re
import subprocess
import sys

import toml  # Ensure 'toml' library is installed to parse pyproject.toml


def is_self_triggered():
    """Check if the latest commit message indicates a version bump to prevent self-trigger."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=True,
        )
        latest_commit_message = result.stdout.strip()
        return "Bump version to" in latest_commit_message
    except subprocess.CalledProcessError as e:
        print("Error retrieving latest commit message:", e)
        return False


def detect_package_manager():
    """Detect the package manager based on project files. Default to pip if Poetry isn't detected."""
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as file:
            pyproject_content = toml.load(file)
            # Check if 'poetry' is in [tool.poetry] to confirm it's a Poetry-based project
            if (
                "tool" in pyproject_content
                and "poetry" in pyproject_content["tool"]
            ):
                return "poetry"

    # Default to pip if Poetry configuration is not found
    return "pip"


def get_current_version_poetry():
    """Retrieve the current version using Poetry."""
    try:
        result = subprocess.run(
            ["poetry", "version", "-s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error fetching current version with Poetry:", e)
        sys.exit(1)


def get_version_file():
    """Identify the primary file used to store version information in a pip-based project."""
    # Check common version file locations
    version_file_names = ["src/__version__.py", "__version__.py", "version.py"]
    for fname in version_file_names:
        if os.path.exists(fname):
            return fname, "file"

    # Check pyproject.toml for Poetry configuration
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as file:
            pyproject_content = toml.load(file)
            if (
                "tool" in pyproject_content
                and "poetry" in pyproject_content["tool"]
            ):
                return "pyproject.toml", "pyproject"

    # Check for setup.py
    if os.path.exists("setup.py"):
        return "setup.py", "setup_py"

    # Check for setup.cfg
    if os.path.exists("setup.cfg"):
        return "setup.cfg", "setup_cfg"

    # If no version source is found, exit with an error
    print(
        "No suitable version file found. Please ensure a version file, pyproject.toml, setup.py, or setup.cfg is present."
    )
    sys.exit(1)


def get_current_version_pip():
    """Retrieve the current version from the identified version source in a pip-based project."""
    version_file, file_type = get_version_file()

    # Retrieve version from common version files
    if file_type == "file":
        with open(version_file, "r") as file:
            content = file.read()
            match = re.search(
                r"^__version__\s*=\s*['\"]([^'\"]+)['\"]",
                content,
                re.MULTILINE,
            )
            if match:
                return match.group(1)

    # Retrieve version from pyproject.toml
    elif file_type == "pyproject":
        with open(version_file, "r") as file:
            pyproject_content = toml.load(file)
            return pyproject_content["tool"]["poetry"]["version"]

    # Retrieve version from setup.py
    elif file_type == "setup_py":
        with open(version_file, "r") as file:
            content = file.read()
            match = re.search(
                r"version\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE
            )
            if match:
                return match.group(1)

    # Retrieve version from setup.cfg
    elif file_type == "setup_cfg":
        with open(version_file, "r") as file:
            content = file.read()
            match = re.search(
                r"^version\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE
            )
            if match:
                return match.group(1)

    print("Version information not found in the detected file.")
    sys.exit(1)


def increment_dev_version(version):
    """Increment the development version for a version string."""
    match = re.match(
        r"^(?P<base>\d+\.\d+\.\d+)(?:-dev(?P<num>\d+))?$", version
    )
    if match:
        base, num = match.group("base"), match.group("num")
        new_version = f"{base}-dev{int(num) + 1 if num else 1}"
        return new_version
    else:
        print(f"Version '{version}' format error.")
        sys.exit(1)


def bump_version_poetry(new_version):
    """Use Poetry to set the new version and return the modified file."""
    try:
        subprocess.run(["poetry", "version", new_version], check=True)
        return "pyproject.toml"
    except subprocess.CalledProcessError as e:
        print("Error bumping version with Poetry:", e)
        sys.exit(1)


def bump_version_pip(new_version):
    """Update the version in the identified version source for pip-based projects and return the modified file."""
    version_file, file_type = get_version_file()

    # Update version in common version files
    if file_type == "file":
        with open(version_file, "r") as file:
            content = file.read()
        new_content = re.sub(
            r"^__version__\s*=\s*['\"][^'\"]+['\"]",
            f"__version__ = '{new_version}'",
            content,
            flags=re.MULTILINE,
        )
        with open(version_file, "w") as file:
            file.write(new_content)
        print(f"Updated version in {version_file} to {new_version}")
        return version_file

    elif file_type == "pyproject":
        with open(version_file, "r") as file:
            pyproject_content = toml.load(file)
        pyproject_content["tool"]["poetry"]["version"] = new_version
        with open(version_file, "w") as file:
            toml.dump(pyproject_content, file)
        print(f"Updated version in pyproject.toml to {new_version}")
        return "pyproject.toml"

    elif file_type == "setup_py":
        with open(version_file, "r") as file:
            content = file.read()
        new_content = re.sub(
            r"version\s*=\s*['\"][^'\"]+['\"]",
            f"version = '{new_version}'",
            content,
            flags=re.MULTILINE,
        )
        with open(version_file, "w") as file:
            file.write(new_content)
        print(f"Updated version in setup.py to {new_version}")
        return "setup.py"

    elif file_type == "setup_cfg":
        with open(version_file, "r") as file:
            content = file.read()
        new_content = re.sub(
            r"^version\s*=\s*['\"][^'\"]+['\"]",
            f"version = '{new_version}'",
            content,
            flags=re.MULTILINE,
        )
        with open(version_file, "w") as file:
            file.write(new_content)
        print(f"Updated version in setup.cfg to {new_version}")
        return "setup.cfg"

    else:
        print("No suitable version file found for pip-based project.")
        sys.exit(1)


def get_latest_git_tag():
    """Retrieve the latest Git tag, if any."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("No tags found in the repository.")
        return None


def version_to_tuple(version):
    """Convert a version string into a tuple of integers and handle -dev suffix."""
    match = re.match(r"(\d+\.\d+\.\d+)(?:-dev(\d+))?", version)
    if match:
        base_version = tuple(map(int, match.group(1).split(".")))
        dev_suffix = int(match.group(2)) if match.group(2) else None
        return base_version, dev_suffix
    else:
        raise ValueError(f"Invalid version format: {version}")


def is_new_version(current_version, latest_tag):
    """Compare current version with the latest Git tag version, handling -dev suffixes correctly."""

    if latest_tag:
        # Strip 'v' from the latest tag and convert both to tuples
        latest_version_tuple, latest_dev = version_to_tuple(
            latest_tag.lstrip("v")
        )
        current_version_tuple, current_dev = version_to_tuple(current_version)

        # Compare base versions first
        if current_version_tuple > latest_version_tuple:
            return True
        elif current_version_tuple < latest_version_tuple:
            return False
        else:
            # If base versions are equal, handle dev suffix comparison
            if current_dev is None:  # current version is stable (e.g., 1.0.0)
                return True
            elif (
                latest_dev is None
            ):  # latest version is stable but current is a dev version
                return False
            else:
                return current_dev > latest_dev  # Compare dev suffixes
    else:
        # No previous tag, so any current version is new
        return True


def commit_and_tag_version(new_version, modified_file):
    """Create a Git tag for the new version, then commit and push the version bump to the repository only if tagging is successful."""
    try:
        # Stage only the modified file
        subprocess.run(["git", "add", modified_file], check=True)

        # Commit the changes with a message
        subprocess.run(
            ["git", "commit", "-m", f"🚀 Bump version to {new_version}"],
            check=True,
        )

        # Attempt to create the new tag
        subprocess.run(["git", "tag", f"v{new_version}"], check=True)
        print(f"Created tag v{new_version}.")

        # Push the tag first to ensure it succeeds
        subprocess.run(
            ["git", "push", "origin", f"v{new_version}"], check=True
        )
        print(f"Pushed tag v{new_version}.")

        # Only push the commit if tag push was successful
        subprocess.run(["git", "push", "origin", "HEAD"], check=True)
        print(f"Committed version bump and pushed to repository.")

    except subprocess.CalledProcessError as e:
        print("Error in tagging or pushing the commit:", e)

        # Clean up: delete the local tag if created but not pushed
        subprocess.run(["git", "tag", "-d", f"v{new_version}"], check=False)

        # Abort with exit status to indicate failure
        sys.exit(1)


def main():
    if is_self_triggered():
        print(
            "Detected self-trigger due to version bump commit. Exiting to prevent loop."
        )
        return

    # Detect package manager
    manager = detect_package_manager()

    # Get current version
    if manager == "poetry":
        current_version = get_current_version_poetry()
    elif manager == "pip":
        current_version = get_current_version_pip()

    # Get the latest Git tag
    latest_tag = get_latest_git_tag()

    # Check if the current version is already a new stable release
    if is_new_version(current_version, latest_tag):
        # Current version is a new release, tag it directly
        print(
            f"Current version {current_version} is a new release compared to latest tag {latest_tag}."
        )
        modified_file = (
            "pyproject.toml" if manager == "poetry" else get_version_file()[0]
        )
        commit_and_tag_version(current_version, modified_file)
    else:
        # Current version matches latest tag, increment to a dev version
        new_version = increment_dev_version(current_version)
        print(
            f"Current version matches latest tag. Incrementing to development version: {new_version}"
        )

        # Determine which file to modify based on package manager
        if manager == "poetry":
            modified_file = bump_version_poetry(new_version)
        elif manager == "pip":
            modified_file = bump_version_pip(new_version)

        # Commit and tag the new dev version
        commit_and_tag_version(new_version, modified_file)


if __name__ == "__main__":
    main()
