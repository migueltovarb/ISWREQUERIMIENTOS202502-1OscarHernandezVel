import os
import sys
import runpy
from pathlib import Path
import django

# iniciador.py
# Iniciador para ejecutar scripts de poblar datos fuera de manage.py
# Colocar este archivo en la raíz del proyecto Django (mismo nivel que manage.py)

def find_project_root(start: Path = None) -> Path:
    """
    Busca hacia arriba un directorio que contenga manage.py y lo devuelve.
    """
    p = start or Path(__file__).resolve().parent
    for parent in [p] + list(p.parents):
        if (parent / "manage.py").exists():
            return parent
    raise FileNotFoundError("No se encontró manage.py en ningún directorio padre.")

def find_settings_module(project_root: Path) -> str:
    """
    Busca settings.py dentro del árbol del proyecto para inferir el módulo de settings.
    Devuelve algo como 'gestion_notas.settings'.
    """
    for settings_path in project_root.rglob("settings.py"):
        # ignorar entornos virtuales típicos
        if "site-packages" in str(settings_path) or "venv" in str(settings_path):
            continue
        rel = settings_path.relative_to(project_root)
        parts = rel.with_suffix("").parts  # e.g. ('gestion_notas','settings')
        return ".".join(parts)
    raise FileNotFoundError("No se encontró settings.py dentro del proyecto.")

def setup_django_env():
    """
    Configura sys.path y DJANGO_SETTINGS_MODULE, luego inicializa Django.
    """
    project_root = find_project_root()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    settings_module = find_settings_module(project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    # Inicializa Django
    try:
        django.setup()
    except Exception as e:
        raise RuntimeError(f"Error al inicializar Django: {e}")

def run_script(script_path: str):
    """
    Ejecuta un script Python (p. ej. scripts/poblar.py) con Django inicializado.
    """
    setup_django_env()
    runpy.run_path(script_path, run_name="__main__")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python iniciador.py ruta/al/script_de_poblar.py")
        sys.exit(1)
    script = sys.argv[1]
    if not Path(script).exists():
        print(f"No existe el script especificado: {script}")
        sys.exit(2)
    run_script(script)