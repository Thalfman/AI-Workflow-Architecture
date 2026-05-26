A

No production workflow covers a monthly partner health report - the only workflow
in `portfolio/workflows.yaml` is `weekly-status-summary`, which rolls up internal
team updates, not partner metrics - so Q1 is no and there is no matching
non-production workflow to resume. The need is plainly recurring (monthly, ahead
of the partner review), so Q4 is yes and this is a new-workflow intake. Route to
`/scope`, which will apply its own reject/defer/merge/one-off/create judgment;
routing only confirms this looks like a genuine new recurring need and hands a
populated intake forward.
