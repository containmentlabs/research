import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
import json

from bench.harness.runner import BenchmarkRunner
from bench.harness.models import TaskConfig
from bench.harness.sweep import SweepRunner

app = typer.Typer(
    name="sock",
    help="S.O.C.K. Benchmark CLI - Run self-replication tasks with optional L.O.C.K. kernel containment",
    no_args_is_help=True,
)
console = Console()


@app.command()
def run(
    task_id: str = typer.Argument(..., help="Task ID to run (e.g., R0-LFD-001)"),
    model: str = typer.Option(..., "--model", "-m", help="Model to evaluate"),
    kernel: Optional[str] = typer.Option(None, "--kernel", "-k", help="Kernel configuration to apply"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Task timeout in seconds"),
    output_dir: Path = typer.Option(Path("./results"), "--output", "-o", help="Output directory for results"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for reproducibility"),
):
    """Run a single benchmark task."""
    console.print(f"[bold blue]Running task:[/bold blue] {task_id}")
    console.print(f"[bold green]Model:[/bold green] {model}")
    if kernel:
        console.print(f"[bold yellow]Kernel:[/bold yellow] {kernel}")
    
    runner = BenchmarkRunner(output_dir=output_dir)
    config = TaskConfig(
        task_id=task_id,
        model=model,
        kernel=kernel,
        timeout=timeout,
        seed=seed,
    )
    
    result = runner.run_task(config)
    console.print(f"[bold]Result:[/bold] {result.status}")
    console.print(f"[bold]R-Score:[/bold] {result.r_score:.3f}")


@app.command("tasks")
def list_tasks():
    """List all available benchmark tasks."""
    tasks_dir = Path("bench/tasks")
    console.print("[bold]Available tasks:[/bold]")
    
    for task_file in sorted(tasks_dir.glob("*.json")):
        task_id = task_file.stem
        console.print(f"  • {task_id}")


@app.command()
def validate():
    """Validate all task definitions against schema."""
    from bench.harness.validator import TaskValidator
    
    validator = TaskValidator()
    results = validator.validate_all()
    
    if results.is_valid:
        console.print("[bold green]✓ All tasks valid[/bold green]")
    else:
        console.print("[bold red]✗ Validation errors found[/bold red]")
        for error in results.errors:
            console.print(f"  • {error}")


@app.command()
def sweep(
    models: str = typer.Argument(..., help="Comma-separated list of models to evaluate"),
    tasks: Optional[str] = typer.Option(None, "--tasks", "-t", help="Comma-separated list of task IDs (default: all)"),
    kernel: Optional[str] = typer.Option(None, "--kernel", "-k", help="Kernel configuration to apply"),
    seeds: str = typer.Option("42", "--seeds", "-s", help="Comma-separated list of random seeds"),
    output_dir: Path = typer.Option(Path("./sweep_results"), "--output", "-o", help="Output directory for results"),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of parallel workers"),
):
    """Run a sweep across multiple models and tasks."""
    model_list = [m.strip() for m in models.split(",")]
    task_list = [t.strip() for t in tasks.split(",")] if tasks else None
    seed_list = [int(s.strip()) for s in seeds.split(",")]
    
    runner = SweepRunner(output_dir, max_workers=workers)
    results = runner.run_sweep(
        models=model_list,
        task_ids=task_list,
        kernel=kernel,
        seeds=seed_list,
    )
    
    runner.summarize_results(results)
    
    summary_file = output_dir / "sweep_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(
            [r.model_dump(mode='json') for r in results],
            f,
            indent=2,
            default=str
        )
    console.print(f"\n[bold green]Results saved to:[/bold green] {summary_file}")


if __name__ == "__main__":
    app() 