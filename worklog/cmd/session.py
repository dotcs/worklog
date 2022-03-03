import typer
from typing import Optional

from worklog.cmd.utils import (
    MutuallyExclusiveGroup,
    configure_worklog,
    offset_minutes_opt,
    time_opt,
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
    log.commit(
        wc.TOKEN_SESSION,
        wc.TOKEN_START,
        offset_min=0 if offset_minutes is None else offset_minutes,
        time=time,
        force=force,
    )


@app.command()
def stop(
    force: bool = _force_opt,
    offset_minutes: Optional[int] = offset_minutes_opt,
    time: Optional[str] = time_opt,
):
    log, cfg = configure_worklog()
    log.commit(
        wc.TOKEN_SESSION,
        wc.TOKEN_STOP,
        offset_min=0 if offset_minutes is None else offset_minutes,
        time=time,
        force=force,
    )


if __name__ == "__main__":
    app()
