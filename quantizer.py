#!/usr/bin/env python3
"""
AllQuants - Comprehensive Model Quantizer
Automates the process of downloading, converting, and quantizing models using Hugging Face and LLAMA.cpp
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json
import re

from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.logging import RichHandler
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.prompt import Confirm
import logging

from huggingface_hub import HfApi, Repository, login, snapshot_download, create_repo
from huggingface_hub.utils import RepositoryNotFoundError
import click


# Configure rich logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("allquants")


@dataclass
class QuantizationConfig:
    """Configuration for quantization types"""
    name: str
    description: str
    size_category: str
    speed: str
    quality: str
    recommended_for: str


class CommandRunner:
    """Central command execution with rich logging and error handling"""
    
    def __init__(self, console: Console):
        self.console = console
        
    def run_command(
        self, 
        cmd: List[str], 
        cwd: Optional[Path] = None,
        description: str = "Running command",
        capture_output: bool = False,
        show_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        Execute a command with rich progress display and logging
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory
            description: Description for progress display
            capture_output: Whether to capture stdout/stderr
            show_output: Whether to show real-time output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd_str = " ".join(str(c) for c in cmd)
        
        with self.console.status(f"[bold blue]{description}[/bold blue]"):
            self.console.print(f"[dim]$ {cmd_str}[/dim]")
            
            if show_output and not capture_output:
                # Real-time output
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                stdout_lines = []
                for line in iter(process.stdout.readline, ''):
                    line = line.rstrip()
                    if line:
                        self.console.print(f"[dim]{line}[/dim]")
                        stdout_lines.append(line)
                
                process.wait()
                return process.returncode, "\n".join(stdout_lines), ""
            
            else:
                # Capture output
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.console.print(f"[red]Command failed with return code {result.returncode}[/red]")
                    if result.stderr:
                        self.console.print(f"[red]Error: {result.stderr}[/red]")
                
                return result.returncode, result.stdout, result.stderr


class ModelQuantizer:
    """Main quantizer class handling the complete workflow"""
    
    # All quantization types from template
    QUANTIZATION_TYPES = [
        QuantizationConfig("Q2_K", "Smallest size, fastest inference, lowest quality", "Smallest", "Fastest", "Low", "Prototyping, minimal RAM/CPU"),
        QuantizationConfig("Q3_K_S", "Very small size, very fast inference", "Very Small", "Very Fast", "Low-Med", "Lightweight devices, testing"),
        QuantizationConfig("Q3_K_M", "Small size, fast inference, medium quality", "Small", "Fast", "Med", "Lightweight, slightly better quality"),
        QuantizationConfig("Q3_K_L", "Small-medium size, fast inference", "Small-Med", "Fast", "Med", "Faster inference, fair quality"),
        QuantizationConfig("Q4_0", "Medium size, good quality", "Medium", "Fast", "Good", "General use, chats, low RAM"),
        QuantizationConfig("Q4_1", "Medium size, slightly better quality", "Medium", "Fast", "Good+", "Recommended, slightly better quality"),
        QuantizationConfig("Q4_K_S", "Medium size, balanced performance", "Medium", "Fast", "Good+", "Recommended, balanced"),
        QuantizationConfig("Q4_K_M", "Medium size, best Q4 option", "Medium", "Fast", "Good++", "Recommended, best Q4 option"),
        QuantizationConfig("Q5_0", "Larger size, very good quality", "Larger", "Moderate", "Very Good", "Chatbots, longer responses"),
        QuantizationConfig("Q5_1", "Larger size, very good+ quality", "Larger", "Moderate", "Very Good+", "More demanding tasks"),
        QuantizationConfig("Q5_K_S", "Larger size, advanced users", "Larger", "Moderate", "Very Good+", "Advanced users, better accuracy"),
        QuantizationConfig("Q5_K_M", "Larger size, excellent quality", "Larger", "Moderate", "Excellent", "Demanding tasks, high quality"),
        QuantizationConfig("Q6_K", "Large size, near FP16 quality", "Large", "Slower", "Near FP16", "Power users, best quantized quality"),
        QuantizationConfig("Q8_0", "Largest size, FP16-like quality", "Largest", "Slowest", "FP16-like", "Maximum quality, high RAM/CPU"),
    ]
    
    def __init__(self, hf_token: Optional[str] = None):
        self.console = Console()
        self.cmd_runner = CommandRunner(self.console)
        self.hf_api = HfApi()
        
        # Setup directories
        self.base_dir = Path.cwd()
        self.models_dir = self.base_dir / "models"
        self.gguf_dir = self.base_dir / "gguf"
        self.quantized_dir = self.base_dir / "quantized"
        
        # Create directories
        for dir_path in [self.models_dir, self.gguf_dir, self.quantized_dir]:
            dir_path.mkdir(exist_ok=True)
            
        # Authenticate with Hugging Face if token provided
        if hf_token:
            login(token=hf_token)
            self.console.print("[green]✓ Logged in to Hugging Face[/green]")
    
    def display_quantization_table(self):
        """Display a beautiful table of quantization options"""
        table = Table(title="Available Quantization Types", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Size", style="green")
        table.add_column("Speed", style="yellow")
        table.add_column("Quality", style="red")
        table.add_column("Recommended For", style="blue")
        
        for config in self.QUANTIZATION_TYPES:
            table.add_row(config.name, config.size_category, config.speed, config.quality, config.recommended_for)
        
        self.console.print(table)
    
    def download_model(self, model_name: str) -> Path:
        """Download model from Hugging Face"""
        model_path = self.models_dir / model_name.replace("/", "_")
        
        if model_path.exists():
            self.console.print(f"[yellow]Model {model_name} already exists at {model_path}[/yellow]")
            return model_path
        
        self.console.print(Panel(f"[bold blue]📥 Downloading Model: {model_name}[/bold blue]", expand=False))
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Downloading {model_name}...", total=100)
                
                # Download model
                snapshot_download(
                    repo_id=model_name,
                    local_dir=model_path
                )
                
                progress.update(task, completed=100)
            
            self.console.print(f"[green]✓ Model downloaded to {model_path}[/green]")
            return model_path
            
        except Exception as e:
            self.console.print(f"[red]✗ Failed to download model: {e}[/red]")
            raise
    
    def convert_to_gguf(self, model_path: Path, model_name: str) -> Path:
        """Convert model to GGUF format using convert.py"""
        gguf_filename = f"{model_name.replace('/', '_')}.gguf"
        gguf_path = self.gguf_dir / gguf_filename
        
        if gguf_path.exists():
            self.console.print(f"[yellow]GGUF file already exists at {gguf_path}[/yellow]")
            return gguf_path
        
        self.console.print(Panel(f"[bold green]🔄 Converting to GGUF: {model_name}[/bold green]", expand=False))
        
        # Use the existing convert.py script
        convert_script = self.base_dir / "convert.py"
        if not convert_script.exists():
            raise FileNotFoundError(f"convert.py not found at {convert_script}")
        
        cmd = [
            sys.executable,
            str(convert_script),
            str(model_path),
            "--outfile", str(gguf_path),
            "--outtype", "f16"
        ]
        
        returncode, stdout, stderr = self.cmd_runner.run_command(
            cmd,
            description=f"Converting {model_name} to GGUF",
            cwd=self.base_dir
        )
        
        if returncode != 0:
            raise RuntimeError(f"GGUF conversion failed: {stderr}")
        
        self.console.print(f"[green]✓ GGUF conversion completed: {gguf_path}[/green]")
        return gguf_path
    
    def quantize_model(self, gguf_path: Path, model_name: str, quant_types: List[str] = None) -> List[Path]:
        """Quantize GGUF model to specified types"""
        if quant_types is None:
            quant_types = [config.name for config in self.QUANTIZATION_TYPES]
        
        self.console.print(Panel(f"[bold yellow]⚡ Quantizing Model: {model_name}[/bold yellow]", expand=False))
        
        # Find llama-quantize executable
        quantize_exe = None
        for exe_name in ["llama-quantize.exe", "llama-quantize"]:
            exe_path = self.base_dir / "llama.cpp.bin" / exe_name
            if exe_path.exists():
                quantize_exe = exe_path
                break
        
        if not quantize_exe:
            raise FileNotFoundError("llama-quantize executable not found in llama.cpp directory")
        
        quantized_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("Quantizing model...", total=len(quant_types))
            
            for i, quant_type in enumerate(quant_types):
                # Create output filename
                base_name = model_name.replace("/", "_")
                output_filename = f"{base_name}-{quant_type.lower()}.gguf"
                output_path = self.quantized_dir / output_filename
                
                if output_path.exists():
                    self.console.print(f"[yellow]Quantized file already exists: {output_path}[/yellow]")
                    quantized_files.append(output_path)
                    progress.update(main_task, advance=1)
                    continue
                
                # Run quantization
                cmd = [
                    str(quantize_exe),
                    str(gguf_path),
                    str(output_path),
                    quant_type
                ]
                
                progress.update(main_task, description=f"Quantizing to {quant_type}...")
                
                returncode, stdout, stderr = self.cmd_runner.run_command(
                    cmd,
                    description=f"Quantizing to {quant_type}",
                    show_output=True
                )
                
                if returncode == 0:
                    quantized_files.append(output_path)
                    self.console.print(f"[green]✓ {quant_type} quantization completed[/green]")
                else:
                    self.console.print(f"[red]✗ {quant_type} quantization failed: {stderr}[/red]")
                
                progress.update(main_task, advance=1)
        
        return quantized_files
    
    def generate_model_card(self, model_name: str, quantized_files: List[Path]) -> str:
        """Generate model card from template"""
        template_path = self.base_dir / "TEMPLATE.md"
        
        if not template_path.exists():
            raise FileNotFoundError("TEMPLATE.md not found")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace template variables
        clean_model_name = model_name.split("/")[-1] if "/" in model_name else model_name
        model_card = template_content.replace("{{base_model}}", clean_model_name)
        model_card = model_card.replace("{{base_model_w_author}}", model_name)
        
        return model_card
    
    def create_and_upload_repo(self, model_name: str, quantized_files: List[Path]) -> str:
        """Create Hugging Face repository and upload quantized models"""
        # Extract just the model name without the original namespace
        clean_model_name = model_name.split("/")[-1] if "/" in model_name else model_name
        repo_name = f"{clean_model_name}-GGUF"
        repo_id = f"leeminwaan/{repo_name}"
        
        self.console.print(Panel(f"[bold cyan]📤 Creating Repository: {repo_id}[/bold cyan]", expand=False))
        
        try:
            # Create repository
            create_repo(repo_id=repo_id, exist_ok=True)
            self.console.print(f"[green]✓ Repository created: {repo_id}[/green]")
            
            # Generate and upload model card
            model_card = self.generate_model_card(model_name, quantized_files)
            self.hf_api.upload_file(
                path_or_fileobj=model_card.encode(),
                path_in_repo="README.md",
                repo_id=repo_id,
                commit_message=f"Add model card for {model_name}"
            )
            
            # Upload quantized files
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                
                upload_task = progress.add_task("Uploading files...", total=len(quantized_files))
                
                for file_path in quantized_files:
                    progress.update(upload_task, description=f"Uploading {file_path.name}...")
                    
                    self.hf_api.upload_file(
                        path_or_fileobj=str(file_path),
                        path_in_repo=file_path.name,
                        repo_id=repo_id,
                        commit_message=f"Add {file_path.name}"
                    )
                    
                    progress.update(upload_task, advance=1)
            
            self.console.print(f"[green]✓ All files uploaded to {repo_id}[/green]")
            return repo_id
            
        except Exception as e:
            self.console.print(f"[red]✗ Failed to create/upload repository: {e}[/red]")
            raise
    
    def quantize_complete_workflow(
        self, 
        model_name: str, 
        hf_token: Optional[str] = None,
        quant_types: Optional[List[str]] = None,
        upload: bool = True,
        interactive: bool = True
    ) -> Dict:
        """Complete quantization workflow with confirmation prompts"""
        
        self.console.print(Panel.fit(
            f"[bold white]AllQuants - Complete Model Quantization Workflow[/bold white]\n"
            f"[cyan]Model: {model_name}[/cyan]",
            border_style="blue"
        ))
        
        results = {
            "model_name": model_name,
            "model_path": None,
            "gguf_path": None,
            "quantized_files": [],
            "repo_id": None,
            "success": False
        }
        
        try:
            # Step 1: Download model
            self.console.print(Panel(
                f"[bold yellow]Step 1: Download Model[/bold yellow]\n"
                f"About to download: [cyan]{model_name}[/cyan]\n"
                f"This will download the full model (potentially several GB)",
                border_style="yellow"
            ))
            
            if interactive and not Confirm.ask("Continue with model download?", default=True):
                self.console.print("[yellow]Workflow cancelled at download step.[/yellow]")
                return results
            
            model_path = self.download_model(model_name)
            results["model_path"] = str(model_path)
            self.console.print(f"[green]Step 1 completed: Model downloaded to {model_path}[/green]\n")
            
            # Step 2: Convert to GGUF
            self.console.print(Panel(
                f"[bold yellow]Step 2: Convert to GGUF[/bold yellow]\n"
                f"About to convert: [cyan]{model_name}[/cyan] to GGUF format\n"
                f"This process may take several minutes depending on model size",
                border_style="yellow"
            ))
            
            if interactive and not Confirm.ask("Continue with GGUF conversion?", default=True):
                self.console.print("[yellow]Workflow cancelled at conversion step.[/yellow]")
                return results
            
            gguf_path = self.convert_to_gguf(model_path, model_name)
            results["gguf_path"] = str(gguf_path)
            self.console.print(f"[green]Step 2 completed: GGUF file created at {gguf_path}[/green]\n")
            
            # Step 3: Quantize
            num_types = len(quant_types) if quant_types else len(self.QUANTIZATION_TYPES)
            self.console.print(Panel(
                f"[bold yellow]Step 3: Quantize Model[/bold yellow]\n"
                f"About to quantize to [cyan]{num_types}[/cyan] different formats\n"
                f"Types: {', '.join(quant_types) if quant_types else 'All 14 types'}\n"
                f"This is the most time-consuming step and may take 30+ minutes",
                border_style="yellow"
            ))
            
            if interactive and not Confirm.ask("Continue with quantization?", default=True):
                self.console.print("[yellow]Workflow cancelled at quantization step.[/yellow]")
                return results
            
            quantized_files = self.quantize_model(gguf_path, model_name, quant_types)
            results["quantized_files"] = [str(f) for f in quantized_files]
            self.console.print(f"[green]Step 3 completed: {len(quantized_files)} quantized files created[/green]\n")
            
            # Step 4: Upload to Hugging Face (if requested)
            if upload and quantized_files:
                self.console.print(Panel(
                    f"[bold yellow]Step 4: Upload to Hugging Face[/bold yellow]\n"
                    f"About to create repository: [cyan]leeminwaan/{model_name}-GGUF[/cyan]\n"
                    f"Will upload [cyan]{len(quantized_files)}[/cyan] quantized files\n"
                    f"This will make the models publicly available",
                    border_style="yellow"
                ))
                
                if interactive and not Confirm.ask("Continue with Hugging Face upload?", default=True):
                    self.console.print("[yellow]Skipping upload step.[/yellow]")
                    results["repo_id"] = "Upload skipped by user"
                else:
                    repo_id = self.create_and_upload_repo(model_name, quantized_files)
                    results["repo_id"] = repo_id
                    self.console.print(f"[green]Step 4 completed: Repository created at {repo_id}[/green]\n")
            
            results["success"] = True
            
            # Final success message
            self.console.print(Panel.fit(
                f"[bold green]Quantization Complete![/bold green]\n"
                f"[white]Model: {model_name}[/white]\n"
                f"[white]Quantized files: {len(quantized_files)}[/white]\n"
                f"[white]Repository: {results.get('repo_id', 'Not uploaded')}[/white]",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Workflow interrupted by user (Ctrl+C).[/yellow]")
            results["error"] = "Interrupted by user"
            return results
        except Exception as e:
            self.console.print(f"[red]Workflow failed: {e}[/red]")
            results["error"] = str(e)
            raise
        
        return results


if __name__ == "__main__":
    # Example usage
    quantizer = ModelQuantizer()
    quantizer.display_quantization_table()
