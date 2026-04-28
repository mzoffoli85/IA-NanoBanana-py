import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

from client import get_client
from steps import generate_image, edit_image, blend_images
from report import generate_report

load_dotenv()

OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)


def _configure_api():
    try:
        get_client()
    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)


def _parse_args():
    parser = argparse.ArgumentParser(description="Nano Banana Studio — PoC de generación y edición de imágenes con IA")
    parser.add_argument("--tema", required=True, help="Concepto en texto libre para generar la imagen")
    parser.add_argument("--edit", dest="edit", default=None, help="Instrucción de edición para el Step 2")
    parser.add_argument("--referencia", default=None, help="Path a imagen local para el blend (Step 3)")
    parser.add_argument(
        "--solo",
        choices=["generate", "edit", "blend"],
        default=None,
        help="Ejecutar solo un step específico",
    )
    return parser.parse_args()


def _validate_args(args):
    if args.solo in ("edit", None) and args.edit is None and args.solo != "generate":
        if args.solo == "edit":
            print("Error: --edit es requerido para el step 'edit'.")
            sys.exit(1)
    if args.solo in ("blend", None) and args.referencia is None:
        if args.solo == "blend":
            print("Error: --referencia es requerido para el step 'blend'.")
            sys.exit(1)


def run_full(args) -> dict:
    results = {}

    print(f"\n[Step 1] Generando imagen desde: \"{args.tema}\"")
    try:
        img_generated, t1 = generate_image(args.tema)
        path1 = OUTPUTS / "01_generated.png"
        img_generated.save(path1)
        results["generate"] = {"prompt": args.tema, "tiempo": t1, "output": str(path1)}
        print(f"  Guardado: {path1}  ({t1}s)")
    except Exception as e:
        print(f"  Error en Step 1: {e}")
        sys.exit(1)

    edit_instruccion = args.edit or "Mejora la imagen manteniendo el estilo original"
    print(f"\n[Step 2] Editando imagen: \"{edit_instruccion}\"")
    try:
        img_edited, t2 = edit_image(img_generated, edit_instruccion)
        path2 = OUTPUTS / "02_edited.png"
        img_edited.save(path2)
        results["edit"] = {"instruccion": edit_instruccion, "tiempo": t2, "output": str(path2)}
        print(f"  Guardado: {path2}  ({t2}s)")
    except Exception as e:
        print(f"  Error en Step 2: {e}")
        sys.exit(1)

    if args.referencia:
        print(f"\n[Step 3] Fusionando con referencia: {args.referencia}")
        try:
            ref_img = Image.open(args.referencia)
            img_blended, t3 = blend_images(img_edited, ref_img)
            path3 = OUTPUTS / "03_blended.png"
            img_blended.save(path3)
            results["blend"] = {"referencia": args.referencia, "tiempo": t3, "output": str(path3)}
            print(f"  Guardado: {path3}  ({t3}s)")
        except Exception as e:
            print(f"  Error en Step 3: {e}")
            sys.exit(1)
    else:
        print("\n[Step 3] Omitido — no se proporcionó --referencia")

    return results


def run_solo(args) -> dict:
    results = {}

    if args.solo == "generate":
        print(f"\n[Step 1] Generando imagen desde: \"{args.tema}\"")
        img, t = generate_image(args.tema)
        path = OUTPUTS / "01_generated.png"
        img.save(path)
        results["generate"] = {"prompt": args.tema, "tiempo": t, "output": str(path)}
        print(f"  Guardado: {path}  ({t}s)")

    elif args.solo == "edit":
        if not args.edit:
            print("Error: --edit es requerido con --solo edit")
            sys.exit(1)
        src = OUTPUTS / "01_generated.png"
        if not src.exists():
            print(f"Error: No se encontró {src}. Ejecuta primero --solo generate.")
            sys.exit(1)
        img_src = Image.open(src)
        print(f"\n[Step 2] Editando imagen: \"{args.edit}\"")
        img, t = edit_image(img_src, args.edit)
        path = OUTPUTS / "02_edited.png"
        img.save(path)
        results["edit"] = {"instruccion": args.edit, "tiempo": t, "output": str(path)}
        print(f"  Guardado: {path}  ({t}s)")

    elif args.solo == "blend":
        if not args.referencia:
            print("Error: --referencia es requerido con --solo blend")
            sys.exit(1)
        src = OUTPUTS / "02_edited.png"
        if not src.exists():
            print(f"Error: No se encontró {src}. Ejecuta primero generate y edit.")
            sys.exit(1)
        img_src = Image.open(src)
        ref_img = Image.open(args.referencia)
        print(f"\n[Step 3] Fusionando con referencia: {args.referencia}")
        img, t = blend_images(img_src, ref_img)
        path = OUTPUTS / "03_blended.png"
        img.save(path)
        results["blend"] = {"referencia": args.referencia, "tiempo": t, "output": str(path)}
        print(f"  Guardado: {path}  ({t}s)")

    return results


def main():
    _configure_api()
    args = _parse_args()
    _validate_args(args)

    print("=== Nano Banana Studio ===")

    results = run_solo(args) if args.solo else run_full(args)

    report_path = generate_report(results, OUTPUTS)
    print(f"\n[Report] Reporte generado: {report_path}")
    print("\n=== Completado ===")


if __name__ == "__main__":
    main()
