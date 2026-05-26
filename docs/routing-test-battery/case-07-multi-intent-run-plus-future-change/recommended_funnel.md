C

This concerns `weekly-status-summary`, which is `status: production` in
`portfolio/workflows.yaml`, so Q1 is yes. The message carries two intents at
once: a normal run of this week's summary (a Funnel B run) and a permanent Risks
Heatmap on every future summary (a Funnel C revision). The decision tree is
top-to-bottom, first-match-wins, and Q2 fires as soon as there is a
future-behavior change, so the request as a whole routes to C - the safer
outcome, since baking the heatmap into this week's run alone would either
silently change future behavior or silently drop a permanent ask. Open the
revision contract-first with `/revise-workflow weekly-status-summary`. The
this-week run is not lost: split the request and run this week's summary under
the current contract now, or queue a Funnel B run once the revision lands.
