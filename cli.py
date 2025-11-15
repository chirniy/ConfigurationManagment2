import sys
import os
from repo_reader import get_direct_dependencies


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

    if not cfg.get("use_test_repo", False):
        print("\nПолучение прямых зависимостей...")

        try:
            deps = get_direct_dependencies(cfg["repository"], cfg["package_name"])
        except Exception as e:
            print(f"[ОШИБКА ПОЛУЧЕНИЯ ЗАВИСИМОСТЕЙ] {e}")
            sys.exit(4)

        if deps:
            print("Прямые зависимости:")
            for d in deps:
                print(f" - {d}")
        else:
            print("У пакета нет прямых зависимостей.")
    else:
        print("\nТестовый режим на Этапе 2 не используется.")


if __name__ == "__main__":
    main()