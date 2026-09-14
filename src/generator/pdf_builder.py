import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from src.generator.girocode import generate_girocode_svg
from src.generator.hybrid_builder import create_hybrid_pdf


def compile_typst_pdf(
    data: Dict[str, Any],
    output_pdf_path: Path,
    base_dir: Path,
    xml_path: Optional[Path] = None,
    create_hybrid: bool = False
) -> Path:
    """
    Compiles the invoice data into a PDF via Typst and optionally embeds the EN16931 XML (Factur-X).
    Maintains lossless full TrueColor quality for logos and embedded graphics.
    """
    template_path = base_dir / "templates" / "typst" / "invoice.typ"
    if not template_path.exists():
        raise FileNotFoundError(f"Typst-Template nicht gefunden: {template_path}")

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = base_dir / "output" / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    inv_id = str(data["invoice"].get("id", "temp")).replace("/", "_").replace("\\", "_")
    
    # 1. Use clean root-relative logo path (lossless full quality)
    data_to_render = dict(data)
    logo_val = data.get("logo_path", "/assets/logo.png")
    if not str(logo_val).startswith("/"):
        logo_val = "/" + str(logo_val).lstrip("/")
    data_to_render["logo_path"] = logo_val

    # 2. Generate GiroCode SVG if applicable
    girocode_svg_path = temp_dir / f"girocode_{inv_id}.svg"
    generated_giro = generate_girocode_svg(data, girocode_svg_path)
    
    if generated_giro and generated_giro.exists():
        data_to_render["girocode_path"] = "/" + generated_giro.relative_to(base_dir).as_posix()
    else:
        data_to_render["girocode_path"] = None

    temp_data_file = temp_dir / f"data_{inv_id}.json"
    with open(temp_data_file, "w", encoding="utf-8") as f:
        json.dump(data_to_render, f, ensure_ascii=False, indent=2)

    try:
        root_rel_path = "/" + temp_data_file.relative_to(base_dir).as_posix()
        cmd = [
            "typst",
            "compile",
            "--root", str(base_dir),
            "--pdf-standard", "a-3b",
            str(template_path),
            str(output_pdf_path),
            "--input", f"data_file={root_rel_path}"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Typst-Fehler ({result.returncode}):\n{result.stderr}\n{result.stdout}")

        # 3. Hybrid embedding if requested
        if create_hybrid and xml_path and xml_path.exists():
            hybrid_pdf_path = output_pdf_path.parent / f"{output_pdf_path.stem}_factur-x.pdf"
            create_hybrid_pdf(
                input_pdf_path=output_pdf_path,
                xml_path=xml_path,
                output_pdf_path=hybrid_pdf_path
            )
            
        return output_pdf_path
            
    finally:
        # Clean up temporary JSON & GiroCode SVG
        if temp_data_file.exists():
            try:
                temp_data_file.unlink()
            except Exception:
                pass
        if girocode_svg_path.exists():
            try:
                girocode_svg_path.unlink()
            except Exception:
                pass
