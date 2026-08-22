import urllib.request
import re
from datetime import datetime, timedelta

def get_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return [], 0

    # Extract dates and counts or levels
    # Pattern looks for tooltips or data-date with count
    days = []
    # Find all table cells with data-date
    pattern = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*>.*?(\d+|No)\s+contribution', re.DOTALL)
    matches = pattern.findall(html)
    
    if not matches:
        # Fallback regex for data-level
        fallback_pattern = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"')
        dates = fallback_pattern.findall(html)
        levels = re.findall(r'data-level="(\d+)"', html)
        for i, d in enumerate(dates):
            lvl = int(levels[i]) if i < len(levels) else 0
            cnt = 1 if lvl > 0 else 0
            days.append((datetime.strptime(d, "%Y-%m-%d").date(), cnt))
    else:
        for d_str, count_str in matches:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            cnt = 0 if count_str == 'No' else int(count_str)
            days.append((d, cnt))
            
    days.sort(key=lambda x: x[0])
    total_contribs = sum(c for _, c in days)
    return days, total_contribs

def calculate_streaks(days):
    if not days:
        return 0, 0, "No contributions"
        
    day_map = {d: c for d, c in days}
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Calculate current streak
    curr_streak = 0
    check_day = today
    if day_map.get(today, 0) == 0:
        check_day = yesterday
        
    while day_map.get(check_day, 0) > 0:
        curr_streak += 1
        check_day -= timedelta(days=1)
        
    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    for d, c in days:
        if c > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    return curr_streak, longest_streak

def generate_svg(total, curr, longest, output_path):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" fill="none">
  <rect width="495" height="195" rx="10" fill="#120E24" stroke="#00E5FF" stroke-width="1"/>
  
  <!-- Total Contributions Section -->
  <g transform="translate(85, 95)" text-anchor="middle">
    <text y="-25" fill="#00E5FF" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="28" font-weight="700">{total}</text>
    <text y="5" fill="#E0E6ED" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="14" font-weight="600">Total Contributions</text>
    <text y="25" fill="#7E8B9B" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11">Yearly Overview</text>
  </g>

  <line x1="170" y1="35" x2="170" y2="160" stroke="#251F3D" stroke-width="1"/>

  <!-- Current Streak Section -->
  <g transform="translate(247, 95)" text-anchor="middle">
    <circle cx="0" cy="-30" r="26" fill="#1B1536" stroke="#00E5FF" stroke-width="2"/>
    <path d="M-6 -22 C-6 -34 6 -32 6 -40 C10 -34 8 -22 -6 -22 Z" fill="#FF2A85"/>
    <text y="-22" fill="#00E5FF" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="28" font-weight="700">{curr}</text>
    <text y="15" fill="#00E5FF" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="14" font-weight="700">Current Streak</text>
    <text y="35" fill="#00E5FF" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11">Active Streak Days</text>
  </g>

  <line x1="325" y1="35" x2="325" y2="160" stroke="#251F3D" stroke-width="1"/>

  <!-- Longest Streak Section -->
  <g transform="translate(410, 95)" text-anchor="middle">
    <text y="-25" fill="#00E5FF" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="28" font-weight="700">{longest}</text>
    <text y="5" fill="#E0E6ED" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="14" font-weight="600">Longest Streak</text>
    <text y="25" fill="#7E8B9B" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11">Personal Best (Days)</text>
  </g>
</svg>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    days, total = get_contributions("Knecrow")
    curr, longest = calculate_streaks(days)
    generate_svg(total, curr, longest, "d:/projects/github/Knecrow-repo/assets/streak.svg")
    generate_svg(total, curr, longest, "d:/projects/github/assets/streak.svg")
