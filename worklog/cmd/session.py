import typer
from typing import Optional
from datetime import datetime

from worklog.cmd.utils import (
    MutuallyExclusiveGroup,
    configure_worklog,
    offset_minutes_opt,
    time_opt,
    stdout_log_entry_date_fmt,
)
import worklog.constants as wc

app = typer.Typer()


_force_opt = typer.Option(
    False, "--force", "-f", help="Force command, will auto-stop running tasks."
)


@app.command()
def start(
    force: bool = _force_opt,
    offset_minutes: Optional[int] = offset_minutes_opt,
    time: Optional[str] = time_opt,
):
    log, cfg = configure_worklog()
    dt = log.commit(
        wc.TOKEN_SESSION,
        wc.TOKEN_START,
        offset_min=0 if offset_minutes is None else offset_minutes,
        time=time,
        force=force,
    )
    fmt = stdout_log_entry_date_fmt(dt)
    typer.echo("Session started on {date}".format(date=dt.strftime(fmt)))


@app.command()
def stop(
    force: bool = _force_opt,
    offset_minutes: Optional[int] = offset_minutes_opt,
    time: Optional[str] = time_opt,
):
    log, cfg = configure_worklog()
    dt = log.commit(
        wc.TOKEN_SESSION,
        wc.TOKEN_STOP,
        offset_min=0 if offset_minutes is None else offset_minutes,
        time=time,
        force=force,
    )
    fmt = stdout_log_entry_date_fmt(dt)
    typer.echo("Session stopped on {date}".format(date=dt.strftime(fmt)))


if __name__ == "__main__":
    app()
