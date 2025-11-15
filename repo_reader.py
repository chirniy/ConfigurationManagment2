import urllib.request
import tarfile
import io


def download_apkindex(repo_url):
    url = repo_url.rstrip("/") + "/x86_64/APKINDEX.tar.gz"
    print(f"Скачиваем индекс пакетов: {url}")

    with urllib.request.urlopen(url) as response:
        return response.read()


def parse_apkindex(content_text):
    packages = {}
    current_pkg = None
    deps = []

    for line in content_text.split("\n"):
        line = line.strip()

        if not line:
            if current_pkg:
                packages[current_pkg] = deps
            current_pkg = None
            deps = []
            continue

        if line.startswith("P:"):
            current_pkg = line[2:].strip()

        elif line.startswith("D:") and current_pkg:
            raw = line[2:].strip().split()
            deps = [d.split(">")[0].split("<")[0].split("=")[0] for d in raw]

    return packages


def get_direct_dependencies(repo_url, package_name):
    apkindex_bytes = download_apkindex(repo_url)

    with tarfile.open(fileobj=io.BytesIO(apkindex_bytes), mode="r:gz") as tar:
        member = tar.extractfile("APKINDEX")
        if not member:
            raise RuntimeError("Файл APKINDEX не найден внутри архива!")
        text = member.read().decode("utf-8")

    db = parse_apkindex(text)

    if package_name not in db:
        raise ValueError(f"Пакет '{package_name}' не найден в репозитории!")

    return db[package_name]