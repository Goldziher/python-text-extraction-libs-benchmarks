#!/usr/bin/env python3
"""Script to check minimal installation sizes of text extraction libraries."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def get_package_size(package_name: str, extra_deps: list[str] | None = None) -> dict[str, Any]:
    """Get the installation size of a package in a clean environment."""
    print(f"Checking installation size for: {package_name}")

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "test_env"

        try:
            # Create virtual environment
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True, capture_output=True)

            # Get pip path
            if sys.platform == "win32":
                pip_path = venv_path / "Scripts" / "pip"
                python_path = venv_path / "Scripts" / "python"
            else:
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"

            # Install package
            install_cmd = [str(pip_path), "install", package_name]
            if extra_deps:
                install_cmd.extend(extra_deps)

            result = subprocess.run(install_cmd, check=False, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Failed to install {package_name}: {result.stderr}")
                return {"error": result.stderr}

            # Get site-packages size
            site_packages = (
                venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            )
            if not site_packages.exists():
                # Try alternative path for some systems
                site_packages = venv_path / "Lib" / "site-packages"

            if site_packages.exists():
                total_size = sum(f.stat().st_size for f in site_packages.rglob("*") if f.is_file())
                size_mb = total_size / (1024 * 1024)

                # Get list of installed packages
                list_result = subprocess.run(
                    [str(pip_path), "list", "--format=json"], check=False, capture_output=True, text=True
                )
                packages = json.loads(list_result.stdout) if list_result.returncode == 0 else []

                return {
                    "size_bytes": total_size,
                    "size_mb": round(size_mb, 2),
                    "packages": packages,
                    "package_count": len(packages),
                }
            return {"error": "Could not find site-packages directory"}

        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}


def main() -> None:
    """Check installation sizes for all text extraction libraries."""
    libraries = {
        "kreuzberg": {"package": "kreuzberg", "description": "Comprehensive text extraction library"},
        "docling": {"package": "docling", "description": "IBM's document processing library"},
        "markitdown": {"package": "markitdown", "description": "Microsoft's markdown converter"},
        "unstructured": {"package": "unstructured", "description": "Unstructured.io document processing"},
        "pymupdf": {"package": "pymupdf", "description": "Fast PDF text extraction with PyMuPDF"},
        "pdfplumber": {"package": "pdfplumber", "description": "Specialized PDF table extraction"},
    }

    results = {}

    for lib_name, lib_info in libraries.items():
        print(f"\n{'=' * 50}")
        print(f"Testing {lib_name} ({lib_info['description']})")
        print(f"{'=' * 50}")

        size_info = get_package_size(lib_info["package"])
        results[lib_name] = {"package": lib_info["package"], "description": lib_info["description"], **size_info}

        if "error" in size_info:
            print(f"❌ Error: {size_info['error']}")
        else:
            print(f"✅ Size: {size_info['size_mb']} MB")
            print(f"📦 Dependencies: {size_info['package_count']} packages")

    # Print summary
    print(f"\n{'=' * 70}")
    print("INSTALLATION SIZE SUMMARY")
    print(f"{'=' * 70}")

    successful_results = [(name, data) for name, data in results.items() if "error" not in data]
    successful_results.sort(key=lambda x: x[1]["size_mb"])

    print(f"{'Library':<15} {'Size (MB)':<12} {'Dependencies':<12} {'Description'}")
    print("-" * 70)

    for lib_name, data in successful_results:
        print(f"{lib_name:<15} {data['size_mb']:<12} {data['package_count']:<12} {data['description']}")

    # Show errors
    error_results = [(name, data) for name, data in results.items() if "error" in data]
    if error_results:
        print("\n❌ Failed installations:")
        for lib_name, data in error_results:
            print(f"  {lib_name}: {data['error']}")

    # Save detailed results
    with open("installation_sizes.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Detailed results saved to: installation_sizes.json")


if __name__ == "__main__":
    main()
