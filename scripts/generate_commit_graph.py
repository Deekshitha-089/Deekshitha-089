
import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

GRAPHQL_URL = "https://api.github.com/graphql"

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=364)


def fetch_contribution_data():
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "username": USERNAME,
            "from": START_DATE.isoformat() + "T00:00:00Z",
            "to": END_DATE.isoformat() + "T23:59:59Z",
        },
    }

    request = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME,
        },
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise RuntimeError(result["errors"])

    user = result.get("data", {}).get("user")

    if user is None:
        raise RuntimeError("GitHub user was not found.")

    calendar = user["contributionsCollection"]["contributionCalendar"]

    contributions = {}

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            contributions[day["date"]] = day["contributionCount"]

    return contributions


def generate_svg(contributions):
    width = 1200
    height = 440

    left = 75
    right = 35
    top = 95
    bottom = 75

    graph_width = width - left - right
    graph_height = height - top - bottom

    dates = []
    counts = []

    current = START_DATE

    while current <= END_DATE:
        dates.append(current)
        counts.append(contributions.get(current.isoformat(), 0))
        current += timedelta(days=1)

    total = sum(counts)
    peak = max(counts) if counts else 0

    # Dynamic Y-axis scaling
    max_count = max(5, peak)
    step = max(1, (max_count + 4) // 5)
    axis_max = step * 5

    points = []

    for index, count in enumerate(counts):
        x = left + (
            index / max(len(counts) - 1, 1)
        ) * graph_width

        y = top + graph_height - (
            count / axis_max
        ) * graph_height

        points.append((x, y))

    line_points = " ".join(
        f"{x:.2f},{y:.2f}" for x, y in points
    )

    area_points = (
        f"{left},{top + graph_height} "
        + line_points
        + f" {left + graph_width},{top + graph_height}"
    )

    # Horizontal gridlines and Y-axis labels
    grid = []

    for value in range(0, axis_max + 1, step):
        y = top + graph_height - (
            value / axis_max
        ) * graph_height

        grid.append(f"""
        <line
            x1="{left}"
            y1="{y:.2f}"
            x2="{left + graph_width}"
            y2="{y:.2f}"
            stroke="#49203F"
            stroke-width="1"
            opacity="0.65"
        />

        <text
            x="{left - 18}"
            y="{y + 4:.2f}"
            text-anchor="end"
            fill="#C58BB9"
            font-family="monospace"
            font-size="12"
        >{value}</text>
        """)

    # Month labels
    month_labels = []

    previous_month = None

    for index, current_date in enumerate(dates):
        if current_date.month != previous_month:
            x = points[index][0]

            month_labels.append(f"""
            <text
                x="{x:.2f}"
                y="{height - 32}"
                text-anchor="middle"
                fill="#E6A5D5"
                font-family="monospace"
                font-size="12"
            >{current_date.strftime("%b")}</text>
            """)

            previous_month = current_date.month

    # Daily glowing points with hover tooltips
    markers = []

    for index, (x, y) in enumerate(points):
        count = counts[index]
        formatted_date = dates[index].strftime("%d %b %Y")

        tooltip = escape(
            f"{formatted_date}: {count} contributions"
        )

        markers.append(f"""
        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="2.5"
            fill="#FF4FC3"
            opacity="0.8"
        >
            <title>{tooltip}</title>
        </circle>
        """)

    first_date = START_DATE.strftime("%b %Y")
    last_date = END_DATE.strftime("%b %Y")

    svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="Daily GitHub contribution activity graph"
    >

    <defs>

        <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#100018"/>
            <stop offset="100%" stop-color="#08000F"/>
        </linearGradient>

        <linearGradient id="pinkArea" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FF4FC3" stop-opacity="0.38"/>
            <stop offset="65%" stop-color="#FF4FC3" stop-opacity="0.10"/>
            <stop offset="100%" stop-color="#FF4FC3" stop-opacity="0.01"/>
        </linearGradient>

        <linearGradient id="neonLine" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#FF8ADD"/>
            <stop offset="50%" stop-color="#FF35BB"/>
            <stop offset="100%" stop-color="#FF8ADD"/>
        </linearGradient>

        <filter id="pinkGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="7" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3"/>
        </filter>

    </defs>

    <rect
        width="{width}"
        height="{height}"
        rx="20"
        fill="url(#background)"
    />

    <!-- Heading -->

    <text
        x="{left}"
        y="42"
        fill="#FF4FC3"
        font-family="monospace"
        font-size="22"
        font-weight="bold"
        letter-spacing="2"
    >COMMIT ACTIVITY</text>

    <text
        x="{left}"
        y="65"
        fill="#B58AAE"
        font-family="monospace"
        font-size="11"
        letter-spacing="2"
    >DAILY GITHUB CONTRIBUTIONS • LAST 365 DAYS</text>

    <text
        x="{width - right}"
        y="42"
        text-anchor="end"
        fill="#FFFFFF"
        font-family="monospace"
        font-size="20"
        font-weight="bold"
    >{total:,}</text>

    <text
        x="{width - right}"
        y="63"
        text-anchor="end"
        fill="#B58AAE"
        font-family="monospace"
        font-size="11"
    >TOTAL CONTRIBUTIONS</text>

    <!-- Grid -->

    {''.join(grid)}

    <!-- Gradient area -->

    <polygon
        points="{area_points}"
        fill="url(#pinkArea)"
    />

    <!-- Blurred neon glow -->

    <polyline
        points="{line_points}"
        fill="none"
        stroke="#FF4FC3"
        stroke-width="10"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.65"
        filter="url(#softGlow)"
    />

    <!-- Main neon line -->

    <polyline
        points="{line_points}"
        fill="none"
        stroke="url(#neonLine)"
        stroke-width="3"
        stroke-linecap="round"
        stroke-linejoin="round"
        filter="url(#pinkGlow)"
    />

    <!-- Daily points -->

    {''.join(markers)}

    <!-- X-axis -->

    {''.join(month_labels)}

    <text
        x="{left}"
        y="{height - 10}"
        fill="#9E7297"
        font-family="monospace"
        font-size="10"
    >{first_date}</text>

    <text
        x="{width - right}"
        y="{height - 10}"
        text-anchor="end"
        fill="#9E7297"
        font-family="monospace"
        font-size="10"
    >{last_date}</text>

    </svg>
    """

    output_path = Path("assets/commit-activity.svg")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(svg, encoding="utf-8")

    print(f"Generated graph: {output_path}")
    print(f"Total contributions: {total}")
    print(f"Peak daily contributions: {peak}")


def main():
    contributions = fetch_contribution_data()
    generate_svg(contributions)


if __name__ == "__main__":
    main()
