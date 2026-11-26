# news-image-20261126-entry

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/shelbyxxx1/news-image-20261126-entry/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/shelbyxxx1/news-image-20261126-entry/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

The World in One Day — a broadsheet front page that sums up the world news of Thursday, 26 November 2026 in a single 1024 × 1024 image. `render.py` typesets and draws the whole page with Pillow from a fixed, date-checked news brief: a masthead with the day's date, Houthi missiles over Riyadh as the lead with a drawn night-sky interception illustration, two medium stories (US tariffs on 14 partners; the Cairo tanker fire), a six-number strip, a dot-matrix world map with numbered pins, 34 more dated briefs, and a DATE CHECK box — no downloaded assets, fully deterministic. The graded entrypoint `main.py` uses only the Python standard library: it copies the committed `entry.png` into the output directory.

## How to run

```sh
python3 render.py   # redraw entry.png from the brief (local only; needs Pillow + DejaVu/Noto fonts)
python3 main.py     # copy entry.png to /output (or $MAKEFUN_OUTPUT_DIR)
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=rtcpv23d&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
