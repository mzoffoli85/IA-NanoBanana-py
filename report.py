from datetime import datetime
from pathlib import Path


def generate_report(results: dict, output_dir: Path) -> Path:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M")

    total = sum(
        v["tiempo"] for v in results.values() if isinstance(v, dict) and "tiempo" in v
    )

    lines = [
        "# Nano Banana Studio — Reporte",
        f"**Fecha:** {datetime_str}",
        "",
    ]

    if "generate" in results:
        r = results["generate"]
        lines += [
            "## Step 1 — Generate",
            f'**Prompt:** "{r["prompt"]}"',
            f'**Tiempo:** {r["tiempo"]}s',
            f'**Output:** {r["output"]}',
            "",
        ]

    if "edit" in results:
        r = results["edit"]
        lines += [
            "## Step 2 — Edit",
            f'**Instrucción:** "{r["instruccion"]}"',
            f'**Tiempo:** {r["tiempo"]}s',
            f'**Output:** {r["output"]}',
            "",
        ]

    if "blend" in results:
        r = results["blend"]
        lines += [
            "## Step 3 — Blend",
            f'**Referencia:** {r["referencia"]}',
            f'**Tiempo:** {r["tiempo"]}s',
            f'**Output:** {r["output"]}',
            "",
        ]

    done = {k: "✅" for k in ["generate", "edit", "blend"] if k in results}
    skipped = {k: "⏭️" for k in ["generate", "edit", "blend"] if k not in results}
    status = {**done, **skipped}

    lines += [
        "## Resumen",
        f"- **Total:** {round(total, 2)}s",
        f"- **Imágenes generadas:** {len(done)}",
        (
            f"- **Capacidades demostradas:** "
            f"text-to-image {status['generate']} | "
            f"edición {status['edit']} | "
            f"blend {status['blend']}"
        ),
    ]

    report_path = output_dir / f"report_{date_str}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
