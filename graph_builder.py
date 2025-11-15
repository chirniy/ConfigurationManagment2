class DependencyGraph:
    def __init__(self, dependencies):
        self.graph = dependencies

    def get_transitive_dependencies(self, pkg_name):
        visited = set()
        result = []

        def dfs(pkg):
            if pkg in visited:
                return
            visited.add(pkg)
            for dep in self.graph.get(pkg, []):
                dfs(dep)
            result.append(pkg)

        dfs(pkg_name)
        result.remove(pkg_name)
        return result


def load_test_repo(path):
    dependencies = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise ValueError(f"Неверная строка в тестовом репозитории: {line}")
            pkg, deps = line.split(":", 1)
            pkg = pkg.strip()
            deps = [d.strip() for d in deps.split() if d.strip()]
            dependencies[pkg] = deps
    return dependencies