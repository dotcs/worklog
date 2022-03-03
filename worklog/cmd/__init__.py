import typer
from typing import Optional
from datetime import datetime, timezone, timedelta
import re

from worklog.cmd.doctor import app as doctor_app
from worklog.cmd.log import app as log_app
from worklog.cmd.report import app as report_app
from worklog.cmd.session import app as session_app
from worklog.cmd.status import app as status_app
from worklog.cmd.task import app as task_app
from worklog.cmd.utils import configure_worklog
from worklog.constants import Category
import worklog.constants as wc

app = typer.Typer()

now = datetime.now(timezone.utc).astimezone(tz=wc.LOCAL_TIMEZONE).replace(microsecond=0)
current_month: str = now.replace(day=1).isoformat()[: len("2000-01-01")]
next_month: str = (now.replace(day=1) + timedelta(days=31)).replace(day=1).isoformat()[
    : len("2000-01-01")
]


def _positive_int(value: int):
    if value < 0:
        raise typer.BadParameter("Value must be larger or equal to zero")
    return value


def _combined_month_or_day_or_week_parser(value: str) -> str:
    if re.match(r"^\d{4}\-\d{2}$", value):
        return _year_month_parser(value).isoformat()
    elif re.match(r"^\d{4}\-\d{2}\-\d{2}$", value):
        return _year_month_day_parser(value).isoformat()
    elif re.match(r"^\d{4}-W\d{2}$", value):
        return _calendar_week_parser(value).isoformat()
    raise typer.BadParameter(f"{value} is not a valid format")


def _year_month_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}\-\d{2}$", value):
        raise typer.BadParameter(f"{value} is not in the format YYYY-MM")
    year, month = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=1, tzinfo=wc.LOCAL_TIMEZONE)


def _year_month_day_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}\-\d{2}\-\d{2}$", value):
        raise typer.BadParameter(f"{value} is not in the format YYYY-MM-DD")
    year, month, day = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=day, tzinfo=wc.LOCAL_TIMEZONE)


def _calendar_week_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}-W\d{2}$", value):
        raise typer.BadParameter(f"{value} is not in the format cwWW")
    dt = datetime.strptime(value + "-1", "%Y-W%W-%w").replace(tzinfo=wc.LOCAL_TIMEZONE)
    return dt


@app.callback()
def callback():
    """Simple CLI tool to log work and projects."""


@app.command()
def doctor():
    """
    The doctor command checks the worklog for missing or problematic entries. \
    It will report the following issues: non-closed working sessions.
    """
    log, _ = configure_worklog()
    log.doctor()


@app.command()
def log(
    number: int = typer.Option(
        10,
        "--number",
        "-n",
        help="Defines many log entries should be shown. System pager will be used if n > 20.",
        callback=_positive_int,
    ),
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Show all entries. System pager will be used.",
    ),
    category: Category = typer.Option(None, help="Filter category"),
    pager: bool = typer.Option(
        True,
        help=(
            "Use a the system pager. "
            "Prints all output to STDOUT regardless of how many entries will be shown. "
            "This flag should be used if there are problems with the system pager."
        ),
    ),
):
    """Shows the content of the worklog file sorted after the date and time of \
    the entry. Use this command to manually review the content of the \
    worklog."""
    log, cfg = configure_worklog()
    no_pager_max_entries = int(cfg.get("worklog", "no_pager_max_entries"))
    use_pager = pager and (show_all or number > no_pager_max_entries)
    category_str: Optional[str] = None if not category else category.value
    if not show_all:
        log.log(number, use_pager, category_str)
    else:
        log.log(-1, use_pager, category_str)


@app.command()
def report(
    date_from: str = typer.Option(
        current_month,
        callback=_combined_month_or_day_or_week_parser,
        help=(
            "Date from which the aggregation should be started (inclusive). "
            "By default the start of the current calendar month is selected. "
            "Allowed input formats are YYYY-MM-DD, YYYY-MM and YYYY-WXX, with "
            "XX referring to the week number, e.g. 35."
        ),
    ),
    date_to: str = typer.Option(
        next_month,
        callback=_combined_month_or_day_or_week_parser,
        help=(
            "Date to which the aggregation should be started (exclusive). "
            "By default the next calendar month is selected. "
            "Allowed input formats are YYYY-MM-DD, YYYY-MM and YYYY-WXX, with "
            "XX referring to the week number, e.g. 35."
        ),
    ),
):
    """
    Creates a report for a given time window. Working time will be aggregated on a \
    monthly, weekly and daily basis. Tasks will be aggregated separately. By \
    default the current month will be used for the report.
    """
    log, _ = configure_worklog()
    dt_date_from = datetime.fromisoformat(date_from)
    dt_date_to = datetime.fromisoformat(date_to)
    log.report(dt_date_from, dt_date_to)


app.add_typer(
    session_app,
    name="session",
    help="""\
    Commit the start or end of a new working session to the worklog file. \
    Use this function to stamp in the morning and stamp out in the \
    evening.""",
)
app.add_typer(
    status_app,
    name="status",
    help="""\
    Creates a report for a given time window. Working time will be aggregated on \
    a monthly, weekly and daily basis. Tasks will be aggregated separately. By \
    default the current month will be used for the report.
    """,
)
app.add_typer(
    task_app,
    name="task",
    help="""\
    Tasks are pieces of work to be done or undertaken. A task can only be \
    started during an ongoing session. Use 'wl session start' to start a new \
    working session.""",
)


if __name__ == "__main__":
    app()
