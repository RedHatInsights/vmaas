# Hermetic Build Process

This document outlines the steps to create a hermetic build environment by generating RPM lock files and Python requirements files using the provided Makefile targets. The process ensures reproducible builds by locking dependencies for both system (RPM) and Python packages. Follow the steps below, committing changes to `git` after each section to track progress.

## Generating RPM Lock Files

To generate the RPM lock file (`rpms.lock.yaml`), follow these steps to create the necessary repository configuration and package lists.

### Step 1: Generate the `ubi.repo` File
Run the `generate-repo-file` target to create the `ubi.repo` file, which configures the UBI (Universal Base Image) repositories for RPM packages.

```bash
make generate-repo-file
```

- **Input**: Uses `BASE_IMAGE` (default: `registry.access.redhat.com/ubi9/ubi-minimal:latest`).
- **Output**: Creates `ubi.repo` with enabled x86_64 repositories.
- **Optional**: Specify a custom image with `BASE_IMAGE`, e.g., `make generate-repo-file BASE_IMAGE=registry.access.redhat.com/ubi9/ubi:latest`.

### Step 2: Generate the `rpms.in.yaml` File
Run the `generate-rpms-in-yaml` target to extract RPM packages from the `CONTAINERFILE` and create `rpms.in.yaml`.

```bash
make generate-rpms-in-yaml
```

- **Input**: Uses `CONTAINERFILE` (default: `Dockerfile`) to parse `yum`, `dnf`, or `microdnf install` commands.
- **Output**: Creates `rpms.in.yaml` listing RPM packages, repository files, and architecture.
- **Optional**: Specify a custom file with `CONTAINERFILE`, e.g., `make generate-rpms-in-yaml CONTAINERFILE=Containerfile`.

### Step 3: Generate the `rpms.lock.yaml` File
Run the `generate-rpm-lockfile` target to create the locked RPM dependency file using the `rpm-lockfile-prototype` tool.

If your Dockerfile/Containerfile uses other repo than UBI e.g. Copr, you need to create <repo_name>.repo and update repofiles values in rpms.in.yaml to include <repo_name>.repo.

```bash
make generate-rpm-lockfile
```

- **Input**: Requires `rpms.in.yaml` and `BASE_IMAGE`.
- **Output**: Creates `rpms.lock.yaml` with locked RPM versions.
- **Optional**: Use a custom `BASE_IMAGE` as in Step 1.

### Commit Changes
After completing the RPM lock file steps, commit the generated files to `git`:

```bash
git add rpms.in.yaml rpms.lock.yaml
git commit -m "Add generated RPM lock files"
```

## Generating Python Requirements Files

To generate the Python requirements files (`requirements.txt`, `requirements-build.in`, `requirements-build.txt`), follow these steps to lock application and build dependencies.

### Step 1: Generate the `requirements.txt` File
Run the `generate-requirements-txt` target to create `requirements.txt` from Poetry or Pipenv lock files.

```bash
make generate-requirements-txt
```

- **Input**: Uses `poetry.lock` or `Pipfile.lock` if present; exits successfully if `requirements.txt` already exists.
- **Output**: Creates `requirements.txt` with application dependencies.
- **Error**: Fails if no lock file is found and `requirements.txt` is missing.

### Step 2: Generate the `requirements-build.in` File
Run the `generate-requirements-build-in` target to create `requirements-build.in` from the `[build-system]` section of `pyproject.toml`.

```bash
make generate-requirements-build-in
```

- **Input**: Parses `pyproject.toml` for `[build-system].requires`.
- **Output**: Creates `requirements-build.in` with build dependencies (e.g., `poetry-core==2.1.3`).
- **Manual Step**: If additional build dependencies are discovered (e.g., during testing), update `.hermetic_builds/add_manual_build_dependencies.sh` (if it exists) to append them. Each entry should be:

  ```bash
  echo "<package>==<version>" >> requirements-build.in
  ```

  Example:
  ```bash
  echo "setuptools==68.2.2" >> requirements-build.in
  ```

  If this script doesn’t exist, manually edit `requirements-build.in` or create the script in `.hermetic_builds`.

### Step 3: Generate the `requirements-build.txt` File
Run the `generate-requirements-build-txt` target to create `requirements-build.txt` with locked build dependencies using a containerized environment.

```bash
make generate-requirements-build-txt
```

- **Input**: Requires `requirements.txt` and scripts `.hermetic_builds/prep_dependencies.sh` and `.hermetic_builds/generate_requirements_build.sh`.
- **Output**: Creates `requirements-build.in` (updated) and `requirements-build.txt` with locked dependencies and hashes.
- **Customization**:
  - Ensure `.hermetic_builds/prep_dependencies.sh` installs `wget` and sets up `pip/pip3` and `python/python3` commands. If the `BASE_IMAGE` or environment changes, adjust the script to include necessary packages (e.g., `python3.12`, `python3.12-pip`, `wget`). Example snippet:
    ```bash
    microdnf install -y python3.12 python3.12-pip wget
    ln -s $(which python3.12) /usr/local/bin/python3
    ln -s $(which pip3.12) /usr/local/bin/pip3
    ```
  - Verify both scripts are executable (`chmod +x .hermetic_builds/*.sh`).
- **Optional**: Specify a custom `BASE_IMAGE`, e.g., `make generate-requirements-build-txt BASE_IMAGE=registry.access.redhat.com/ubi9/ubi:latest`.

### Commit Changes
After completing the Python requirements steps, commit the generated files and any script updates to `git`:

```bash
git add requirements.txt requirements-build.in requirements-build.txt .hermetic_builds/*.sh
git commit -m "Add generated Python requirements files and hermetic build scripts"
```

## Notes
- **Git Commits**: Commit after each section to maintain a clear history of changes.
- **Dependencies**: Ensure `podman` is installed and network access is available for PyPI and GitHub.
- **Scripts**: The `.hermetic_builds` scripts are user-maintained. Create or update them as needed for your project.
- **Errors**: Check error messages from `make` targets for guidance (e.g., missing files, container failures).
- **BASE_IMAGE**: Defaults to `registry.access.redhat.com/ubi9/ubi-minimal:latest`. Adjust as needed for compatibility.
