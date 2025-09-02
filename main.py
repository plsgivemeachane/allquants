#!/usr/bin/env python3
"""
AllQuants CLI - Command Line Interface for Model Quantization
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from quantizer import ModelQuantizer


console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="AllQuants")
def cli():
    """AllQuants - Comprehensive Model Quantizer using Hugging Face and LLAMA.cpp"""
    pass


@cli.command()
@click.argument('model_name')
@click.option('--hf-token', envvar='HF_TOKEN', help='Hugging Face token (or set HF_TOKEN env var)')
@click.option('--quant-types', multiple=True, help='Specific quantization types (e.g., Q4_K_M Q8_0)')
@click.option('--no-upload', is_flag=True, help='Skip uploading to Hugging Face')
@click.option('--show-types', is_flag=True, help='Show available quantization types')
@click.option('--non-interactive', is_flag=True, help='Run without confirmation prompts')
def quantize(model_name: str, hf_token: Optional[str], quant_types: tuple, no_upload: bool, show_types: bool, non_interactive: bool):
    """Quantize a model from Hugging Face"""
    
    try:
        quantizer = ModelQuantizer(hf_token=hf_token)
        
        if show_types:
            quantizer.display_quantization_table()
            return
        
        # Validate model name
        if not model_name or '/' not in model_name:
            console.print("[red]Error: Model name must be in format 'organization/model-name'[/red]")
            sys.exit(1)
        
        # Convert quant_types tuple to list, or use all types
        selected_types = list(quant_types) if quant_types else None
        
        # Confirm before starting
        if not no_upload and not hf_token:
            console.print("[yellow]Warning: No Hugging Face token provided. Models will not be uploaded.[/yellow]")
            no_upload = True
        
        console.print(Panel.fit(
            f"[bold]Starting quantization workflow[/bold]\n"
            f"Model: [cyan]{model_name}[/cyan]\n"
            f"Quantization types: [yellow]{len(selected_types) if selected_types else 14}[/yellow]\n"
            f"Upload to HF: [{'green' if not no_upload else 'red'}]{not no_upload}[/{'green' if not no_upload else 'red'}]\n"
            f"Interactive mode: [{'green' if not non_interactive else 'yellow'}]{not non_interactive}[/{'green' if not non_interactive else 'yellow'}]"
        ))
        
        if not non_interactive and not Confirm.ask("Continue with quantization?", default=True):
            console.print("[yellow]Quantization cancelled.[/yellow]")
            return
        
        # Run the complete workflow
        results = quantizer.quantize_complete_workflow(
            model_name=model_name,
            hf_token=hf_token,
            quant_types=selected_types,
            upload=not no_upload,
            interactive=not non_interactive
        )
        
        # Display results summary
        console.print(Panel.fit(
            f"[bold green]✅ Quantization Results[/bold green]\n"
            f"Model: {results['model_name']}\n"
            f"Quantized files: {len(results['quantized_files'])}\n"
            f"Repository: {results.get('repo_id', 'Not uploaded')}\n"
            f"Success: {'✅' if results['success'] else '❌'}"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Quantization interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def types():
    """Show all available quantization types"""
    quantizer = ModelQuantizer()
    quantizer.display_quantization_table()


@cli.command()
@click.argument('model_name')
@click.option('--hf-token', envvar='HF_TOKEN', help='Hugging Face token')
def download(model_name: str, hf_token: Optional[str]):
    """Download a model from Hugging Face"""
    try:
        quantizer = ModelQuantizer(hf_token=hf_token)
        model_path = quantizer.download_model(model_name)
        console.print(f"[green]✅ Model downloaded to: {model_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error downloading model: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.argument('model_name')
def convert(model_path: str, model_name: str):
    """Convert a downloaded model to GGUF format"""
    try:
        quantizer = ModelQuantizer()
        gguf_path = quantizer.convert_to_gguf(Path(model_path), model_name)
        console.print(f"[green]✅ GGUF file created: {gguf_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error converting model: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--check-deps', is_flag=True, help='Check if all dependencies are available')
def setup(check_deps):
    """Setup and verify AllQuants environment"""
    console.print(Panel.fit("[bold blue]AllQuants Environment Setup[/bold blue]"))
    
    # Check Python version
    python_version = sys.version_info
    console.print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        console.print("[red]X Python 3.8+ required[/red]")
        return
    else:
        console.print("[green]OK Python version OK[/green]")
    
    # Check for required files
    base_dir = Path.cwd()
    required_files = ['convert.py', 'TEMPLATE.md', 'requirements.txt']
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            console.print(f"[green]OK {file_name} found[/green]")
        else:
            console.print(f"[red]X {file_name} missing[/red]")
    
    # Check for llama.cpp directory and executables
    llama_dir = base_dir / "llama.cpp.bin"
    if llama_dir.exists():
        console.print("[green]OK llama.cpp directory found[/green]")
        
        # Check for quantize executable
        quantize_exe = None
        for exe_name in ["llama-quantize.exe", "llama-quantize"]:
            exe_path = llama_dir / exe_name
            if exe_path.exists():
                quantize_exe = exe_path
                break
        
        if quantize_exe:
            console.print(f"[green]OK llama-quantize found: {quantize_exe.name}[/green]")
        else:
            console.print("[red]X llama-quantize executable not found[/red]")
            console.print("[yellow]Please build llama.cpp with quantization support[/yellow]")
    else:
        console.print("[red]X llama.cpp directory not found[/red]")
    
    # Check dependencies if requested
    if check_deps:
        console.print("\n[bold]Checking Python dependencies...[/bold]")
        try:
            import huggingface_hub
            import transformers
            import torch
            import rich
            import click
            console.print("[green]OK All Python dependencies available[/green]")
        except ImportError as e:
            console.print(f"[red]X Missing dependency: {e}[/red]")
            console.print("[yellow]Run: pip install -r requirements.txt[/yellow]")
    
    console.print("\n[bold green]Setup check complete![/bold green]")


if __name__ == '__main__':
    cli()