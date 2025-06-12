import typer
from pathlib import Path
from typing import List, Optional
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from bench.harness.runner import BenchmarkRunner
from bench.harness.models import TaskConfig, TaskResult
from bench.harness.validator import TaskValidator

console = Console()


class SweepRunner:
    def __init__(self, output_dir: Path, max_workers: int = 4):
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.runner = BenchmarkRunner(output_dir)
        self.validator = TaskValidator()
        
    def run_sweep(
        self,
        models: List[str],
        task_ids: Optional[List[str]] = None,
        kernel: Optional[str] = None,
        seeds: List[int] = [42],
        timeout: int = 300,
    ) -> List[TaskResult]:
        if task_ids is None:
            task_ids = [f.stem for f in Path("bench/tasks").glob("*.json")]
            
        total_runs = len(models) * len(task_ids) * len(seeds)
        console.print(f"[bold]Starting sweep:[/bold] {total_runs} total runs")
        console.print(f"  Models: {', '.join(models)}")
        console.print(f"  Tasks: {', '.join(task_ids)}")
        console.print(f"  Seeds: {seeds}")
        if kernel:
            console.print(f"  Kernel: {kernel}")
            
        configs = []
        for model in models:
            for task_id in task_ids:
                for seed in seeds:
                    configs.append(TaskConfig(
                        task_id=task_id,
                        model=model,
                        kernel=kernel,
                        timeout=timeout,
                        seed=seed,
                    ))
                    
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running benchmarks...", total=total_runs)
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_config = {
                    executor.submit(self.runner.run_task, config): config
                    for config in configs
                }
                
                for future in as_completed(future_to_config):
                    config = future_to_config[future]
                    try:
                        result = future.result()
                        results.append(result)
                        progress.update(
                            task,
                            advance=1,
                            description=f"Completed {config.task_id} on {config.model}"
                        )
                    except Exception as e:
                        console.print(f"[red]Error running {config.task_id} on {config.model}: {e}[/red]")
                        progress.update(task, advance=1)
                        
        return results
    
    def summarize_results(self, results: List[TaskResult]):
        table = Table(title="Sweep Results Summary")
        table.add_column("Model", style="cyan")
        table.add_column("Task", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("R-Score", style="yellow")
        table.add_column("Time (s)", style="blue")
        
        for result in sorted(results, key=lambda r: (r.model, r.task_id)):
            status_style = "green" if result.status == "success" else "red"
            table.add_row(
                result.model,
                result.task_id,
                f"[{status_style}]{result.status}[/{status_style}]",
                f"{result.r_score:.3f}",
                f"{result.execution_time:.2f}"
            )
            
        console.print(table)
        
        avg_scores = {}
        for result in results:
            if result.model not in avg_scores:
                avg_scores[result.model] = []
            avg_scores[result.model].append(result.r_score)
            
        console.print("\n[bold]Average R-Scores by Model:[/bold]")
        for model, scores in sorted(avg_scores.items()):
            avg = sum(scores) / len(scores)
            console.print(f"  {model}: {avg:.3f}")


def run_sweep_cli(
    models: List[str],
    tasks: Optional[List[str]] = None,
    kernel: Optional[str] = None,
    seeds: str = "42",
    output_dir: Path = Path("./sweep_results"),
    workers: int = 4,
):
    """Run a sweep across multiple models and tasks."""
    seed_list = [int(s) for s in seeds.split(",")]
    
    runner = SweepRunner(output_dir, max_workers=workers)
    results = runner.run_sweep(
        models=models,
        task_ids=tasks,
        kernel=kernel,
        seeds=seed_list,
    )
    
    runner.summarize_results(results)
    
    summary_file = output_dir / "sweep.json"
    with open(summary_file, 'w') as f:
        json.dump(
            [r.model_dump(mode='json') for r in results],
            f,
            indent=2,
            default=str
        )
    console.print(f"\n[bold green]Results saved to:[/bold green] {summary_file}")


if __name__ == "__main__":
    typer.run(run_sweep_cli) 