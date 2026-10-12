import json
import urllib.error
import urllib.request

PYPI_URL = "https://pypi.org/pypi/{}/json"


def fetch_json(url):
    """Return the parsed JSON at url, or None on a 404."""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def parse_requirements(path):
    """Yield (name, version) pairs from a requirements file of name==version lines."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, version = line.split("==", 1)
            yield name.strip(), version.strip()


def main():
    checked = 0
    missing_packages = []
    missing_versions = []
    found = []  # (upload_time, name, version)

    for name, version in parse_requirements("requirements.txt"):
        checked += 1

        package = fetch_json(PYPI_URL.format(name))
        if package is None:
            missing_packages.append(name)
            continue

        files = package.get("releases", {}).get(version)
        if not files:
            missing_versions.append(f"{name}=={version}")
            continue

        found.append((files[0]["upload_time"], name, version))

    print(f"Dependencies checked: {checked}")
    print(f"Packages not on PyPI: {len(missing_packages)}")
    print(f"Versions not on PyPI: {len(missing_versions)}")

    if found:
        upload_time, name, version = min(found)
        print(f"Oldest pinned release: {name}=={version} ({upload_time[:4]})")
    else:
        print("Oldest pinned release: none")


if __name__ == "__main__":
    main()
