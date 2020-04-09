```bash
wl commit start
wl commit start --offset-minutes -5
wl commit stop
wl commit stop --offset-minutes +5

wl log
wl log -n 30
wl log --all

wl status
wl status --yesterday
wl status --fmt "{percentage}"

wl doctor
```

```
$ wl status today
You are currently clocked in
Total time: 7.2h
End of day: 2020-04-08 17:23
```

Planned

```bash
wl task create <NAME>
wl task list
wl task delete <NAME>
wl commit start --task <taskID>

wl report --today
wl report --yesterday
wl report --current-month
wl report --last-month
wl report --month 2020-04
wl report --date 2020-04-08

wl config get working_time.daily_hours
wl config set working_time.daily_hours 8

wl edit 2020-04-08
```