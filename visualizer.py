import subprocess
import tempfile
import os

def generate_dot(graph_dict):
    lines = ["digraph dependencies {"]
    for pkg, deps in graph_dict.items():
        for dep in deps:
            lines.append(f'    "{pkg}" -> "{dep}";')
        if not deps:
            lines.append(f'    "{pkg}";')
    lines.append("}")
    return "\n".join(lines)


def render_graph(dot_text, output_file="graph.png"):
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".dot") as f:
        f.write(dot_text)
        dot_file = f.name

    try:
        subprocess.run(["dot", "-Tpng", dot_file, "-o", output_file], check=True)
        print(f"Граф сохранён в {output_file}")
    except Exception as e:
        print(f"[ОШИБКА РИСОВАНИЯ ГРАФА] {e}")
    finally:
        os.unlink(dot_file)


def print_ascii_tree(graph_dict, root, indent="", visited=None):
    if visited is None:
        visited = set()
    if root in visited:
        print(indent + root + " (цикл)")
        return
    visited.add(root)
    print(indent + root)
    for dep in graph_dict.get(root, []):
        print_ascii_tree(graph_dict, dep, indent + "  ", visited)