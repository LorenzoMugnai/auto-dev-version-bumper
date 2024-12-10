# auto-dev-version-bumper

`auto-dev-version-bumper` is a GitHub Action that automates version bumping for Python projects in a development environment. It is designed to handle version increments for `develop` branches and automatically creates development (`-dev`) versions if needed. The workflow will:

- Check the current version against the latest Git tag.
- Automatically bump the version as a `-dev` version if the current version matches the latest tag.
- Create a new release tag if the current version is already a stable upgrade from the latest tag.

This action is intended to run on development branches to streamline version management and ensure version continuity during development cycles.

## How It Works


1. **Check if it needs to run**
   - Checks if the latest commit contains "Bump version to" or "no bump". If so, the Action is not activated.

2. **Detects the Package Manager**:
   - Checks if the project uses `Poetry` or a `pip`-based setup to manage versioning.
   - Supports common version sources such as `pyproject.toml`, `setup.py`, `setup.cfg`, `version` or `__version__.py`.

3. **Compares Versions**:
   - Retrieves the latest Git tag to determine the last tagged version.
   - Compares the current version in the code with the latest Git tag:
     - If the current version is higher than the latest tag, it’s tagged directly as a new stable release.
     - If the current version matches the latest tag, it increments to a `-dev` version.

4. **Commits and Tags the New Version**:
   - After determining the appropriate version (either new stable or `-dev`), it **creates a new commit with the version update** and generates a Git tag.
   - The commit message will indicate the version change (e.g., "Bump version to 1.0.1-dev1"), providing a clear version history in the repository.

This action is intended to run on development branches to streamline version management and ensure version continuity during development cycles.

## Usage

Add the `auto-dev-version-bumper` action to your development branch workflow. It will automatically detect the appropriate version file, compare it with the latest tag, and handle version updates accordingly.

### Example Workflow Configuration

```yaml
name: Auto Dev Version Bumper

on:
  push:
    branches:
      - develop

jobs:
  version-bump:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 

      - name: Run auto-dev-version-bumper
        uses: LorenzoMugnai/auto-dev-version-bumper@v1.1
        with:
          dev_suffix: "-beta"  # Optional: Customize the development suffix (defaults to "-dev")
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
          GITHUB_SHA: ${{ github.event.after }}
```

## Inputs

- **`dev_suffix`** (optional): specifies the suffix for development versions. Default is `-dev`. You can customize this suffix to match your project's versioning scheme (e.g., `-beta`, `-alpha`, etc.).

> [!WARNING]
> Workflow Triggering: Be cautious when using `auto-dev-version-bumper` on branches that perform automatic pushes, as this can inadvertently cause an infinite loop of workflow triggers. The action itself commits and pushes new versions, which may trigger subsequent workflows if not properly configured. To prevent this, add a condition to your workflow to skip runs initiated by version bump commits. For example, you can check the commit message to ensure the workflow only triggers on non-bump commits. This setup is crucial for ensuring smooth operation on development branches without risking self-triggering loops. See the example below for reference.

>```yaml
>name: Auto Dev Version Bumper
>
>on:
>  push:
>    branches:
>      - develop
>
>jobs:
>  version-bump:
>    if: ${{ !contains(github.event.head_commit.message, 'Bump version to') }} 
>    runs-on: ubuntu-latest
>    steps:
>      - name: Checkout repository
>        uses: actions/checkout@v4
>        with:
>          fetch-depth: 0 
>
>      - name: Run auto-dev-version-bumper
>        uses: LorenzoMugnai/auto-dev-version-bumper@v1.1
>        with:
>          dev_suffix: "-beta"  # Optional: Customize the development suffix (defaults to "-dev")
>        env:
>          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Pass GITHUB_TOKEN explicitly
>          GITHUB_SHA: ${{ github.event.after }} # Pass the commit SHA
>```

## Version Bumping Rules

The action follows these rules for version comparison and bumping:

- **New Stable Version**: If the current version is greater than the latest Git tag, it will be tagged as a new stable release.
- **Development Version (`-dev`)**:
  - If the current version matches the latest Git tag (both base version and dev suffix), the version will increment as a `-dev` version (e.g., `1.0.0` → `1.0.0-dev1`).
  - If the current version already has a `-dev` suffix that matches the latest tag, the `-dev` version suffix will be further incremented.

## Examples

### Case 1: stable release to first development version

- **Current Version**: `1.0.1`
- **Latest Tag**: `1.0.1`
- **Outcome**: The action creates a new `-dev` version and tags it as `1.0.1-dev1` to signify continued development.

### Case 2: incrementing a development version

- **Current Version**: `1.0.1-dev1`
- **Latest Tag**: `1.0.1-dev1`
- **Outcome**: The current version matches the latest tag exactly, so the action updates the version to `1.0.1-dev2`, creates a tag and pushes the changes.

### Case 3: development to new stable release

- **Current Version**: `1.0.1`
- **Latest Tag**: `1.0.0-dev4`
- **Outcome**: `1.0.1` is recognized as a new stable release (higher than `1.0.0-dev4`). The action tags `1.0.1` as the new version.

### Case 4: stable release to next stable release

- **Current Version**: `1.0.2`
- **Latest Tag**: `1.0.1`
- **Outcome**: `1.0.2` is recognized as a new stable release (higher than `1.0.1`). The action tags `1.0.2` as the new version.

## Notes

- This action is intended for use on **development branches only**, as it increments versions with `-dev` suffixes for ongoing development.
- **Stable tags** should ideally be created only on release branches to avoid mixing stable and development versions.
