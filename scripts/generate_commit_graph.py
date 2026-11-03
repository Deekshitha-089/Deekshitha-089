import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path

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

    calendar = result["data"]["user"]["contributionsCollection"][
        "contributionCalendar"
    ]

    contributions = {}

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            contributions[day["date"]] = day["contributionCount"]

    return contributions


def generate_svg(contributions):
    width = 1000
    height = 320

    left = 55
    right = 25
    top = 45
    bottom = 55

    graph_width = width - left - right
    graph_height = height - top - bottom

    counts = []

    current = START_DATE

    while current <= END_DATE:
        counts.append(contributions.get(current.isoformat(), 0))
        current += timedelta(days=1)

    max_count = max(counts) if counts else 1
    max_count = max(max_count, 1)

    points = []

    for index, count in enumerate(counts):
        x = left + (index / max(len(counts) - 1, 1)) * graph_width
        y = top + graph_height - (count / max_count) * graph_height
        points.append(f"{x:.2f},{y:.2f}")

    polyline_points = " ".join(points)

    area_points = (
        f"{left},{top + graph_height} "
        + polyline_points
        + f" {left + graph_width},{top + graph_height}"
    )

    total = sum(counts)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
      <linearGradient id="pinkArea" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF4FC3" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#FF4FC3" stop-opacity="0.02"/>
      </linearGradient>
    </defs>

    <rect width="100%" height="100%" fill="#0D0014" rx="18"/>

    <text x="{left}" y="28"
      fill="#FF4FC3"
      font-family="monospace"
      font-size="18"
      font-weight="bold">
      COMMIT ACTIVITY
    </text>

    <text x="{width - right}" y="28"
      text-anchor="end"
      fill="#FFFFFF"
      font-family="monospace"
      font-size="13">
      {total} contributions in the last year
    </text>

    <polygon points="{area_points}" fill="url(#pinkArea)"/>

    <polyline points="{polyline_points}"
      fill="none"
      stroke="#FF4FC3"
      stroke-width="3"
      stroke-linecap="round"
      stroke-linejoin="round"/>

    <text x="{left}" y="{height - 20}"
      fill="#FF4FC3"
      font-family="monospace"
      font-size="12">
      {START_DATE.strftime("%b %Y")}
    </text>

    <text x="{width - right}" y="{height - 20}"
      text-anchor="end"
      fill="#FF4FC3"
      font-family="monospace"
      font-size="12">
      {END_DATE.strftime("%b %Y")}
    </text>
    </svg>
    """

    output_path = Path("assets/commit-activity.svg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")

    print(f"Generated graph: {output_path}")


def main():
    contributions = fetch_contribution_data()
    generate_svg(contributions)


if __name__ == "__main__":
    main()