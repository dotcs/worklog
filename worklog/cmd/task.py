import typer
from typing import Optional

from worklog.cmd.utils import (
    configure_worklog,
    offset_minutes_opt,
    time_opt,
    configure_worklog,
)
from worklog.utils.time import calc_log_time
import worklog.constants as wc

app = typer.Typer()


@app.command()
def start(
    task_id: str = typer.Argument(..., help="Task identifier, can be freely chosen"),
    auto_stop: bool = typer.Option(
        False, "--auto-stop", "-as", help="Automatically stops open tasks.",
    ),
    offset_minutes: Optional[int] = offset_minutes_opt,
    time: Optional[str] = time_opt,
):
    log, _ = configure_worklog()

    offset_min = 0 if offset_minutes is None else offset_minutes

    if auto_stop:
        commit_dt = calc_log_time(offset_min, time)
        stopped_tasks = log.stop_active_tasks(commit_dt)

    log.commit(
        wc.TOKEN_TASK,
        wc.TOKEN_START,
        offset_min=offset_min,
        time=time,
        identifier=task_id,
    )


@app.command()
def stop(
    task_id: str = typer.Argument(..., help="Task identifier of a running task"),
    offset_minutes: Optional[int] = offset_minutes_opt,
    time: Optional[str] = time_opt,
):
    log, _ = configure_worklog()

    offset_min = 0 if offset_minutes is None else offset_minutes

    log.commit(
        wc.TOKEN_TASK,
        wc.TOKEN_STOP,
        offset_min=offset_min,
        time=time,
        identifier=task_id,
    )


@app.command()
def list():
    log, _ = configure_worklog()
    log.list_tasks()


@app.command()
def report(
    task_id: str = typer.Argument(..., help="Task identifier of a recorded task"),
):
    log, _ = configure_worklog()
    log.task_report(task_id)


if __name__ == "__main__":
    app()
