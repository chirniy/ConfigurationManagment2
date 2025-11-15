import sys
import os
from repo_reader import get_direct_dependencies
from graph_builder import DependencyGraph, load_test_repo


def load_simple_yaml(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                raise ValueError(f"Неверная строка в конфиге: '{line.strip()}'")

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False

            data[key] = value

    return data


def validate(cfg):
    errors = []

    if "package_name" not in cfg or not isinstance(cfg["package_name"], str) or not cfg["package_name"]:
        errors.append("package_name: обязательный непустой параметр (строка)")

    if "repository" not in cfg or not isinstance(cfg["repository"], str) or not cfg["repository"]:
        errors.append("repository: обязательная строка")

    if "use_test_repo" in cfg and not isinstance(cfg["use_test_repo"], bool):
        errors.append("use_test_repo: должно быть true/false")

    if "ascii_tree" in cfg and not isinstance(cfg["ascii_tree"], bool):
        errors.append("ascii_tree: должно быть true/false")

    if errors:
        raise ValueError("\n".join(errors))


def print_config(cfg):
    print("Загруженные параметры конфигурации:")
    for key in sorted(cfg.keys()):
        print(f"{key} = {cfg[key]}")


def main():
    config_path = "config.yaml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    try:
        cfg = load_simple_yaml(config_path)
    except Exception as e:
        print(f"[ОШИБКА ЧТЕНИЯ КОНФИГА] {e}", file=sys.stderr)
        sys.exit(2)

    try:
        validate(cfg)
    except Exception as e:
        print(f"[ОШИБКА ВАЛИДАЦИИ]\n{e}", file=sys.stderr)
        sys.exit(3)

    print_config(cfg)

    print("\nПостроение графа зависимостей...")

    if cfg.get("use_test_repo", False):
        if "repository" not in cfg or not os.path.exists(cfg["repository"]):
            print("[ОШИБКА] Укажите существующий путь к тестовому файлу")
            sys.exit(4)
        dependencies = load_test_repo(cfg["repository"])
    else:
        try:
            deps = get_direct_dependencies(cfg["repository"], cfg["package_name"])
            dependencies = {cfg["package_name"]: deps}
        except Exception as e:
            print(f"[ОШИБКА ПОЛУЧЕНИЯ ЗАВИСИМОСТЕЙ] {e}")
            sys.exit(4)

    graph = DependencyGraph(dependencies)

    try:
        transitive = graph.get_transitive_dependencies(cfg["package_name"])
    except Exception as e:
        print(f"[ОШИБКА при DFS] {e}")
        sys.exit(5)

    if transitive:
        print(f"Транзитивные зависимости пакета {cfg['package_name']}:")
        for d in transitive:
            print(f" - {d}")
    else:
        print(f"У пакета {cfg['package_name']} нет транзитивных зависимостей.")

    print("\nПорядок установки пакетов:")

    install_order = graph.get_install_order(cfg["package_name"])
    for pkg in install_order:
        print(" -", pkg)

if __name__ == "__main__":
    main()