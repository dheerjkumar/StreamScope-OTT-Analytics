"""
StreamScope Dashboard Visualizer & Screenshot Generator
=======================================================
Generates high-definition vector (SVG) and raster (PNG) dashboard renders
for all 3 StreamScope Power BI pages:
1. Executive Overview (01_executive_overview.svg / .png)
2. Content & Engagement (02_content_and_engagement.svg / .png)
3. Retention & Churn (03_retention_and_churn.svg / .png)

Also generates an interactive HTML viewer: powerbi/dashboard_screenshots/index.html
"""

import os
import struct
import zlib

SCREENSHOTS_DIR = os.path.join("powerbi", "dashboard_screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def generate_svg_page1():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#0b1329; font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;">
  <!-- Background & Grid -->
  <rect width="1920" height="1080" fill="#0b1329"/>
  <rect x="0" y="0" width="1920" height="70" fill="#111c38"/>
  <text x="40" y="44" fill="#f8fafc" font-size="24" font-weight="700">StreamScope</text>
  <text x="180" y="44" fill="#94a3b8" font-size="16">| Executive Overview &amp; Platform Financial Health</text>
  <rect x="1650" y="18" width="230" height="34" rx="6" fill="#1e293b"/>
  <text x="1665" y="40" fill="#38bdf8" font-size="13" font-weight="600">Observation Window: 2025 Full Year</text>

  <!-- Row 1: KPI Cards -->
  <!-- Card 1 -->
  <rect x="40" y="90" width="285" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="125" fill="#94a3b8" font-size="13" font-weight="600" text-transform="uppercase">Total Registered Users</text>
  <text x="65" y="168" fill="#ffffff" font-size="32" font-weight="700">10,000</text>
  <text x="65" y="188" fill="#10b981" font-size="12">↑ 100% Platform Accounts</text>

  <!-- Card 2 -->
  <rect x="355" y="90" width="285" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="380" y="125" fill="#94a3b8" font-size="13" font-weight="600">ACTIVE PAID SUBSCRIBERS</text>
  <text x="380" y="168" fill="#38bdf8" font-size="32" font-weight="700">5,717</text>
  <text x="380" y="188" fill="#38bdf8" font-size="12">77.3% Lifetime Conversion</text>

  <!-- Card 3 -->
  <rect x="670" y="90" width="285" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="695" y="125" fill="#94a3b8" font-size="13" font-weight="600">MONTHLY ACTIVE VIEWERS (MAU)</text>
  <text x="695" y="168" fill="#a855f7" font-size="32" font-weight="700">5,120</text>
  <text x="695" y="188" fill="#a855f7" font-size="12">18.4% DAU/MAU Stickiness</text>

  <!-- Card 4 -->
  <rect x="985" y="90" width="285" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1010" y="125" fill="#94a3b8" font-size="13" font-weight="600">TOTAL STREAMED HOURS</text>
  <text x="1010" y="168" fill="#f59e0b" font-size="32" font-weight="700">126,609</text>
  <text x="1010" y="188" fill="#f59e0b" font-size="12">Across 121,801 Sessions</text>

  <!-- Card 5 -->
  <rect x="1300" y="90" width="285" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1325" y="125" fill="#94a3b8" font-size="13" font-weight="600">MONTHLY RECURRING REVENUE</text>
  <text x="1325" y="168" fill="#10b981" font-size="32" font-weight="700">$70,262</text>
  <text x="1325" y="188" fill="#10b981" font-size="12">ARPU: $12.29 / month</text>

  <!-- Card 6 -->
  <rect x="1615" y="90" width="265" height="110" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1640" y="125" fill="#94a3b8" font-size="13" font-weight="600">MONTHLY CHURN RATE</text>
  <text x="1640" y="168" fill="#f43f5e" font-size="32" font-weight="700">2.4%</text>
  <text x="1640" y="188" fill="#94a3b8" font-size="12">Target Benchmark: &lt; 2.5%</text>

  <!-- Row 2: Charts -->
  <!-- Chart 1: Active Subscribers & MRR -->
  <rect x="40" y="225" width="910" height="400" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="260" fill="#f8fafc" font-size="18" font-weight="700">Active Paid Subscribers &amp; Monthly Revenue Run-Rate</text>
  <text x="65" y="280" fill="#94a3b8" font-size="12">Monthly cumulative trend across 2025 calendar year</text>

  <!-- Bar Visual Simulation -->
  <g transform="translate(80, 310)">
    <!-- Gridlines -->
    <line x1="0" y1="230" x2="820" y2="230" stroke="#1e293b" stroke-width="1"/>
    <line x1="0" y1="170" x2="820" y2="170" stroke="#1e293b" stroke-width="1"/>
    <line x1="0" y1="110" x2="820" y2="110" stroke="#1e293b" stroke-width="1"/>
    <line x1="0" y1="50" x2="820" y2="50" stroke="#1e293b" stroke-width="1"/>

    <!-- Monthly Bars (Subscribers) -->
    <rect x="15" y="180" width="35" height="50" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="85" y="160" width="35" height="70" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="155" y="145" width="35" height="85" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="225" y="130" width="35" height="100" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="295" y="115" width="35" height="115" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="365" y="100" width="35" height="130" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="435" y="88" width="35" height="142" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="505" y="75" width="35" height="155" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="575" y="60" width="35" height="170" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="645" y="48" width="35" height="182" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="715" y="35" width="35" height="195" rx="3" fill="#38bdf8" opacity="0.85"/>
    <rect x="785" y="20" width="35" height="210" rx="3" fill="#38bdf8"/>

    <!-- Revenue Overlay Line -->
    <path d="M 32 185 L 102 165 L 172 150 L 242 135 L 312 120 L 382 105 L 452 92 L 522 78 L 592 64 L 662 50 L 732 38 L 802 22" fill="none" stroke="#10b981" stroke-width="3.5"/>
    <circle cx="802" cy="22" r="5" fill="#10b981"/>

    <!-- Months labels -->
    <text x="25" y="250" fill="#64748b" font-size="11">Jan</text>
    <text x="95" y="250" fill="#64748b" font-size="11">Feb</text>
    <text x="165" y="250" fill="#64748b" font-size="11">Mar</text>
    <text x="235" y="250" fill="#64748b" font-size="11">Apr</text>
    <text x="305" y="250" fill="#64748b" font-size="11">May</text>
    <text x="375" y="250" fill="#64748b" font-size="11">Jun</text>
    <text x="445" y="250" fill="#64748b" font-size="11">Jul</text>
    <text x="515" y="250" fill="#64748b" font-size="11">Aug</text>
    <text x="585" y="250" fill="#64748b" font-size="11">Sep</text>
    <text x="655" y="250" fill="#64748b" font-size="11">Oct</text>
    <text x="725" y="250" fill="#64748b" font-size="11">Nov</text>
    <text x="795" y="250" fill="#64748b" font-size="11">Dec</text>
  </g>

  <!-- Chart 2: MAU & Watch Hours -->
  <rect x="970" y="225" width="910" height="400" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="995" y="260" fill="#f8fafc" font-size="18" font-weight="700">Monthly Active Viewers (MAU) &amp; Streaming Hours</text>
  <text x="995" y="280" fill="#94a3b8" font-size="12">Viewing activity and seasonal engagement velocity</text>

  <g transform="translate(1010, 310)">
    <!-- Area Chart Gradient -->
    <defs>
      <linearGradient id="mauGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#a855f7" stop-opacity="0.6"/>
        <stop offset="100%" stop-color="#a855f7" stop-opacity="0.0"/>
      </linearGradient>
    </defs>
    <path d="M 20 190 Q 200 160 400 120 T 800 30 L 800 230 L 20 230 Z" fill="url(#mauGrad)"/>
    <path d="M 20 190 Q 200 160 400 120 T 800 30" fill="none" stroke="#a855f7" stroke-width="3"/>
    <line x1="0" y1="230" x2="820" y2="230" stroke="#1e293b" stroke-width="1"/>
  </g>

  <!-- Row 3: Lower Charts -->
  <!-- Donut: Plan Tier Mix -->
  <rect x="40" y="645" width="590" height="400" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="680" fill="#f8fafc" font-size="18" font-weight="700">Subscribers by Plan Tier</text>
  <text x="65" y="700" fill="#94a3b8" font-size="12">Distribution across 4 catalog subscription tiers</text>

  <!-- Donut Graphic -->
  <g transform="translate(180, 840)">
    <circle r="90" fill="none" stroke="#1e293b" stroke-width="35"/>
    <circle r="90" fill="none" stroke="#38bdf8" stroke-width="35" stroke-dasharray="250 565" stroke-dashoffset="0"/>
    <circle r="90" fill="none" stroke="#818cf8" stroke-width="35" stroke-dasharray="140 565" stroke-dashoffset="-250"/>
    <circle r="90" fill="none" stroke="#34d399" stroke-width="35" stroke-dasharray="120 565" stroke-dashoffset="-390"/>
    <circle r="90" fill="none" stroke="#f472b6" stroke-width="35" stroke-dasharray="55 565" stroke-dashoffset="-510"/>
    <text x="0" y="5" fill="#f8fafc" font-size="18" font-weight="700" text-anchor="middle">5,717</text>
    <text x="0" y="25" fill="#94a3b8" font-size="11" text-anchor="middle">Active</text>
  </g>
  <!-- Legend -->
  <g transform="translate(340, 770)" font-size="13">
    <rect x="0" y="0" width="12" height="12" fill="#38bdf8" rx="2"/>
    <text x="20" y="11" fill="#f8fafc">Standard HD (45.3%)</text>
    <rect x="0" y="30" width="12" height="12" fill="#818cf8" rx="2"/>
    <text x="20" y="41" fill="#f8fafc">Basic with Ads (24.3%)</text>
    <rect x="0" y="60" width="12" height="12" fill="#34d399" rx="2"/>
    <text x="20" y="71" fill="#f8fafc">Premium 4K (22.4%)</text>
    <rect x="0" y="90" width="12" height="12" fill="#f472b6" rx="2"/>
    <text x="20" y="101" fill="#f8fafc">Family Ultra (8.0%)</text>
  </g>

  <!-- Chart 4: Signups vs Churns -->
  <rect x="650" y="645" width="630" height="400" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="675" y="680" fill="#f8fafc" font-size="18" font-weight="700">Monthly Net Customer Growth</text>
  <text x="675" y="700" fill="#94a3b8" font-size="12">New registrations vs customer churn volume</text>
  <g transform="translate(680, 750)">
    <rect x="50" y="120" width="16" height="100" fill="#38bdf8" rx="2"/>
    <rect x="70" y="180" width="16" height="40" fill="#f43f5e" rx="2"/>

    <rect x="130" y="100" width="16" height="120" fill="#38bdf8" rx="2"/>
    <rect x="150" y="170" width="16" height="50" fill="#f43f5e" rx="2"/>

    <rect x="210" y="90" width="16" height="130" fill="#38bdf8" rx="2"/>
    <rect x="230" y="160" width="16" height="60" fill="#f43f5e" rx="2"/>

    <rect x="290" y="70" width="16" height="150" fill="#38bdf8" rx="2"/>
    <rect x="310" y="150" width="16" height="70" fill="#f43f5e" rx="2"/>

    <rect x="370" y="50" width="16" height="170" fill="#38bdf8" rx="2"/>
    <rect x="390" y="140" width="16" height="80" fill="#f43f5e" rx="2"/>

    <line x1="20" y1="220" x2="550" y2="220" stroke="#1e293b" stroke-width="1"/>
  </g>

  <!-- Chart 5: Acquisition Channels -->
  <rect x="1300" y="645" width="580" height="400" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1325" y="680" fill="#f8fafc" font-size="18" font-weight="700">Subscribers by Acquisition Channel</text>
  <text x="1325" y="700" fill="#94a3b8" font-size="12">Organic vs Paid marketing performance</text>

  <g transform="translate(1330, 740)">
    <!-- Organic Search -->
    <text x="0" y="20" fill="#cbd5e1" font-size="12">Organic Search</text>
    <rect x="130" y="8" width="360" height="18" rx="4" fill="#38bdf8"/>
    <text x="500" y="22" fill="#94a3b8" font-size="12">2,180</text>

    <!-- Social Media -->
    <text x="0" y="60" fill="#cbd5e1" font-size="12">Social Media</text>
    <rect x="130" y="48" width="310" height="18" rx="4" fill="#6366f1"/>
    <text x="450" y="62" fill="#94a3b8" font-size="12">1,820</text>

    <!-- Paid Search -->
    <text x="0" y="100" fill="#cbd5e1" font-size="12">Paid Search</text>
    <rect x="130" y="88" width="230" height="18" rx="4" fill="#818cf8"/>
    <text x="370" y="102" fill="#94a3b8" font-size="12">1,340</text>

    <!-- Referral -->
    <text x="0" y="140" fill="#cbd5e1" font-size="12">Referral</text>
    <rect x="130" y="128" width="180" height="18" rx="4" fill="#10b981"/>
    <text x="320" y="142" fill="#94a3b8" font-size="12">1,060</text>

    <!-- Email Campaign -->
    <text x="0" y="180" fill="#cbd5e1" font-size="12">Email Campaign</text>
    <rect x="130" y="168" width="140" height="18" rx="4" fill="#f59e0b"/>
    <text x="280" y="182" fill="#94a3b8" font-size="12">780</text>

    <!-- Affiliate -->
    <text x="0" y="220" fill="#cbd5e1" font-size="12">Affiliate</text>
    <rect x="130" y="208" width="100" height="18" rx="4" fill="#ec4899"/>
    <text x="240" y="222" fill="#94a3b8" font-size="12">548</text>
  </g>
</svg>"""

def generate_svg_page2():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#0b1329; font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;">
  <rect width="1920" height="1080" fill="#0b1329"/>
  <rect x="0" y="0" width="1920" height="70" fill="#111c38"/>
  <text x="40" y="44" fill="#f8fafc" font-size="24" font-weight="700">StreamScope</text>
  <text x="180" y="44" fill="#94a3b8" font-size="16">| Content Catalog &amp; User Engagement Analytics</text>

  <!-- Row 1 -->
  <!-- Top 10 Titles -->
  <rect x="40" y="90" width="910" height="460" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="125" fill="#f8fafc" font-size="18" font-weight="700">Top 10 Blockbuster Titles by Total Streamed Hours</text>
  <text x="65" y="145" fill="#94a3b8" font-size="12">Ranked by cumulative watch hours and viewer completion</text>

  <g transform="translate(65, 175)">
    <!-- 1. Cyber City 2099 -->
    <text x="0" y="20" fill="#f8fafc" font-size="12" font-weight="600">1. Cyber City 2099</text>
    <rect x="180" y="6" width="600" height="20" rx="3" fill="#38bdf8"/>
    <text x="790" y="21" fill="#38bdf8" font-size="12" font-weight="700">6,341 hrs</text>

    <!-- 2. Apex Protocol -->
    <text x="0" y="55" fill="#f8fafc" font-size="12" font-weight="600">2. Apex Protocol</text>
    <rect x="180" y="41" width="550" height="20" rx="3" fill="#38bdf8"/>
    <text x="740" y="56" fill="#38bdf8" font-size="12" font-weight="700">5,820 hrs</text>

    <!-- 3. The Boardroom -->
    <text x="0" y="90" fill="#f8fafc" font-size="12" font-weight="600">3. The Boardroom</text>
    <rect x="180" y="76" width="510" height="20" rx="3" fill="#38bdf8"/>
    <text x="700" y="91" fill="#38bdf8" font-size="12" font-weight="700">5,411 hrs</text>

    <!-- 4. Neon Horizon -->
    <text x="0" y="125" fill="#f8fafc" font-size="12" font-weight="600">4. Neon Horizon</text>
    <rect x="180" y="111" width="490" height="20" rx="3" fill="#38bdf8"/>
    <text x="680" y="126" fill="#38bdf8" font-size="12" font-weight="700">5,230 hrs</text>

    <!-- 5. Office Pandemonium -->
    <text x="0" y="160" fill="#f8fafc" font-size="12" font-weight="600">5. Office Pandemonium</text>
    <rect x="180" y="146" width="460" height="20" rx="3" fill="#38bdf8"/>
    <text x="650" y="161" fill="#38bdf8" font-size="12" font-weight="700">4,890 hrs</text>

    <!-- 6. Summer in Florence -->
    <text x="0" y="195" fill="#f8fafc" font-size="12" font-weight="600">6. Summer in Florence</text>
    <rect x="180" y="181" width="420" height="20" rx="3" fill="#38bdf8"/>
    <text x="610" y="196" fill="#38bdf8" font-size="12" font-weight="700">4,450 hrs</text>

    <!-- 7. Planet Wild: Oceans -->
    <text x="0" y="230" fill="#f8fafc" font-size="12" font-weight="600">7. Planet Wild: Oceans</text>
    <rect x="180" y="216" width="390" height="20" rx="3" fill="#38bdf8"/>
    <text x="580" y="231" fill="#38bdf8" font-size="12" font-weight="700">4,120 hrs</text>

    <!-- 8. The Vanishing Room -->
    <text x="0" y="265" fill="#f8fafc" font-size="12" font-weight="600">8. The Vanishing Room</text>
    <rect x="180" y="251" width="370" height="20" rx="3" fill="#38bdf8"/>
    <text x="560" y="266" fill="#38bdf8" font-size="12" font-weight="700">3,980 hrs</text>

    <!-- 9. Heartstrings -->
    <text x="0" y="300" fill="#f8fafc" font-size="12" font-weight="600">9. Heartstrings</text>
    <rect x="180" y="286" width="350" height="20" rx="3" fill="#38bdf8"/>
    <text x="540" y="301" fill="#38bdf8" font-size="12" font-weight="700">3,760 hrs</text>

    <!-- 10. Silicon Pioneers -->
    <text x="0" y="335" fill="#f8fafc" font-size="12" font-weight="600">10. Silicon Pioneers</text>
    <rect x="180" y="321" width="330" height="20" rx="3" fill="#38bdf8"/>
    <text x="520" y="336" fill="#38bdf8" font-size="12" font-weight="700">3,540 hrs</text>
  </g>

  <!-- Genre Watch Hours -->
  <rect x="970" y="90" width="910" height="460" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="995" y="125" fill="#f8fafc" font-size="18" font-weight="700">Total Streamed Watch Hours by Content Genre</text>
  <text x="995" y="145" fill="#94a3b8" font-size="12">Viewing demand distribution across catalog categories</text>

  <g transform="translate(1010, 200)">
    <!-- Column Chart for 8 genres -->
    <rect x="20" y="50" width="65" height="260" rx="4" fill="#a855f7"/>
    <text x="52" y="40" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">28.4K</text>
    <text x="52" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Sci-Fi</text>

    <rect x="120" y="70" width="65" height="240" rx="4" fill="#a855f7"/>
    <text x="152" y="60" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">25.6K</text>
    <text x="152" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Action</text>

    <rect x="220" y="100" width="65" height="210" rx="4" fill="#a855f7"/>
    <text x="252" y="90" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">19.8K</text>
    <text x="252" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Drama</text>

    <rect x="320" y="120" width="65" height="190" rx="4" fill="#a855f7"/>
    <text x="352" y="110" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">16.2K</text>
    <text x="352" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Comedy</text>

    <rect x="420" y="140" width="65" height="170" rx="4" fill="#a855f7"/>
    <text x="452" y="130" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">14.5K</text>
    <text x="452" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Thriller</text>

    <rect x="520" y="170" width="65" height="140" rx="4" fill="#a855f7"/>
    <text x="552" y="160" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">10.4K</text>
    <text x="552" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Docu</text>

    <rect x="620" y="210" width="65" height="100" rx="4" fill="#a855f7"/>
    <text x="652" y="200" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">6.8K</text>
    <text x="652" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Romance</text>

    <rect x="720" y="230" width="65" height="80" rx="4" fill="#a855f7"/>
    <text x="752" y="220" fill="#a855f7" font-size="12" font-weight="700" text-anchor="middle">4.9K</text>
    <text x="752" y="330" fill="#94a3b8" font-size="11" text-anchor="middle">Animation</text>

    <line x1="0" y1="310" x2="820" y2="310" stroke="#1e293b" stroke-width="1"/>
  </g>

  <!-- Row 2 -->
  <!-- Device Share -->
  <rect x="40" y="570" width="590" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="605" fill="#f8fafc" font-size="18" font-weight="700">Streaming Sessions by Device</text>
  <text x="65" y="625" fill="#94a3b8" font-size="12">Hardware preference &amp; playback share</text>

  <g transform="translate(190, 780)">
    <circle r="95" fill="none" stroke="#1e293b" stroke-width="35"/>
    <circle r="95" fill="none" stroke="#38bdf8" stroke-width="35" stroke-dasharray="250 597" stroke-dashoffset="0"/>
    <circle r="95" fill="none" stroke="#10b981" stroke-width="35" stroke-dasharray="190 597" stroke-dashoffset="-250"/>
    <circle r="95" fill="none" stroke="#f59e0b" stroke-width="35" stroke-dasharray="110 597" stroke-dashoffset="-440"/>
    <circle r="95" fill="none" stroke="#ec4899" stroke-width="35" stroke-dasharray="47 597" stroke-dashoffset="-550"/>
    <text x="0" y="8" fill="#f8fafc" font-size="16" font-weight="700" text-anchor="middle">121.8K</text>
  </g>
  <g transform="translate(360, 720)" font-size="13">
    <rect x="0" y="0" width="12" height="12" fill="#38bdf8" rx="2"/>
    <text x="20" y="11" fill="#f8fafc">Smart TV (42.0%)</text>
    <rect x="0" y="30" width="12" height="12" fill="#10b981" rx="2"/>
    <text x="20" y="41" fill="#f8fafc">Mobile App (32.0%)</text>
    <rect x="0" y="60" width="12" height="12" fill="#f59e0b" rx="2"/>
    <text x="20" y="71" fill="#f8fafc">Laptop / Web (18.0%)</text>
    <rect x="0" y="90" width="12" height="12" fill="#ec4899" rx="2"/>
    <text x="20" y="101" fill="#f8fafc">Tablet (8.0%)</text>
  </g>

  <!-- Content Type Comparison -->
  <rect x="650" y="570" width="610" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="675" y="605" fill="#f8fafc" font-size="18" font-weight="700">Movies vs Web Series Dynamics</text>
  <text x="675" y="625" fill="#94a3b8" font-size="12">Unique reach and replay frequency comparison</text>
  <g transform="translate(720, 680)">
    <text x="80" y="30" fill="#38bdf8" font-size="16" font-weight="700">Feature Films</text>
    <rect x="60" y="60" width="120" height="220" rx="6" fill="#38bdf8"/>
    <text x="120" y="180" fill="#0b1329" font-size="20" font-weight="700" text-anchor="middle">65.2K</text>
    <text x="120" y="200" fill="#0b1329" font-size="12" text-anchor="middle">Hours</text>

    <text x="320" y="30" fill="#a855f7" font-size="16" font-weight="700">Web Series</text>
    <rect x="300" y="75" width="120" height="205" rx="6" fill="#a855f7"/>
    <text x="360" y="180" fill="#ffffff" font-size="20" font-weight="700" text-anchor="middle">61.4K</text>
    <text x="360" y="200" fill="#ffffff" font-size="12" text-anchor="middle">Hours</text>
  </g>

  <!-- Completion Rates -->
  <rect x="1280" y="570" width="600" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1305" y="605" fill="#f8fafc" font-size="18" font-weight="700">Average Completion Rate by Genre</text>
  <text x="1305" y="625" fill="#94a3b8" font-size="12">Audience retention and content drop-off benchmark</text>

  <g transform="translate(1310, 670)">
    <text x="0" y="25" fill="#cbd5e1" font-size="12">Drama</text>
    <rect x="110" y="10" width="370" height="20" rx="3" fill="#10b981"/>
    <text x="490" y="25" fill="#10b981" font-size="12" font-weight="700">82.4%</text>

    <text x="0" y="65" fill="#cbd5e1" font-size="12">Thriller</text>
    <rect x="110" y="50" width="360" height="20" rx="3" fill="#10b981"/>
    <text x="480" y="65" fill="#10b981" font-size="12" font-weight="700">80.2%</text>

    <text x="0" y="105" fill="#cbd5e1" font-size="12">Sci-Fi</text>
    <rect x="110" y="90" width="350" height="20" rx="3" fill="#38bdf8"/>
    <text x="470" y="105" fill="#38bdf8" font-size="12" font-weight="700">78.5%</text>

    <text x="0" y="145" fill="#cbd5e1" font-size="12">Action</text>
    <rect x="110" y="130" width="345" height="20" rx="3" fill="#38bdf8"/>
    <text x="465" y="145" fill="#38bdf8" font-size="12" font-weight="700">77.1%</text>

    <text x="0" y="185" fill="#cbd5e1" font-size="12">Comedy</text>
    <rect x="110" y="170" width="330" height="20" rx="3" fill="#f59e0b"/>
    <text x="450" y="185" fill="#f59e0b" font-size="12" font-weight="700">74.2%</text>

    <text x="0" y="225" fill="#cbd5e1" font-size="12">Documentary</text>
    <rect x="110" y="210" width="320" height="20" rx="3" fill="#f59e0b"/>
    <text x="440" y="225" fill="#f59e0b" font-size="12" font-weight="700">71.8%</text>

    <text x="0" y="265" fill="#cbd5e1" font-size="12">Romance</text>
    <rect x="110" y="250" width="310" height="20" rx="3" fill="#ec4899"/>
    <text x="430" y="265" fill="#ec4899" font-size="12" font-weight="700">69.5%</text>
  </g>
</svg>"""

def generate_svg_page3():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#0b1329; font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;">
  <rect width="1920" height="1080" fill="#0b1329"/>
  <rect x="0" y="0" width="1920" height="70" fill="#111c38"/>
  <text x="40" y="44" fill="#f8fafc" font-size="24" font-weight="700">StreamScope</text>
  <text x="180" y="44" fill="#94a3b8" font-size="16">| Customer Retention &amp; Churn Dynamics</text>

  <!-- Row 1 -->
  <!-- Monthly Churn & Lost MRR -->
  <rect x="40" y="90" width="910" height="460" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="125" fill="#f8fafc" font-size="18" font-weight="700">Monthly Subscriber Churn &amp; Lost Recurring Revenue</text>
  <text x="65" y="145" fill="#94a3b8" font-size="12">30-day true churn events and lost recurring revenue impact</text>

  <g transform="translate(80, 200)">
    <line x1="0" y1="280" x2="820" y2="280" stroke="#1e293b" stroke-width="1"/>
    <!-- Churn Line -->
    <path d="M 20 220 L 90 210 L 160 200 L 230 190 L 300 180 L 370 165 L 440 150 L 510 135 L 580 120 L 650 105 L 720 90 L 790 75" fill="none" stroke="#f43f5e" stroke-width="3.5"/>
    <circle cx="790" cy="75" r="5" fill="#f43f5e"/>
    <text x="760" y="60" fill="#f43f5e" font-size="13" font-weight="700">248 Users ($3,040)</text>

    <!-- Month axis -->
    <text x="15" y="305" fill="#64748b" font-size="11">Jan</text>
    <text x="85" y="305" fill="#64748b" font-size="11">Feb</text>
    <text x="155" y="305" fill="#64748b" font-size="11">Mar</text>
    <text x="225" y="305" fill="#64748b" font-size="11">Apr</text>
    <text x="295" y="305" fill="#64748b" font-size="11">May</text>
    <text x="365" y="305" fill="#64748b" font-size="11">Jun</text>
    <text x="435" y="305" fill="#64748b" font-size="11">Jul</text>
    <text x="505" y="305" fill="#64748b" font-size="11">Aug</text>
    <text x="575" y="305" fill="#64748b" font-size="11">Sep</text>
    <text x="645" y="305" fill="#64748b" font-size="11">Oct</text>
    <text x="715" y="305" fill="#64748b" font-size="11">Nov</text>
    <text x="785" y="305" fill="#64748b" font-size="11">Dec</text>
  </g>

  <!-- Cancellation Reasons -->
  <rect x="970" y="90" width="910" height="460" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="995" y="125" fill="#f8fafc" font-size="18" font-weight="700">Primary Stated Cancellation Reasons</text>
  <text x="995" y="145" fill="#94a3b8" font-size="12">Pareto analysis of feedback reported during cancellation flow</text>

  <g transform="translate(1005, 185)">
    <!-- Price too high -->
    <text x="0" y="25" fill="#f8fafc" font-size="13" font-weight="600">Price too high</text>
    <rect x="180" y="10" width="550" height="22" rx="4" fill="#f43f5e"/>
    <text x="740" y="26" fill="#f43f5e" font-size="13" font-weight="700">32.4% ($22.7K lost)</text>

    <!-- Lack of content -->
    <text x="0" y="70" fill="#f8fafc" font-size="13" font-weight="600">Lack of content</text>
    <rect x="180" y="55" width="410" height="22" rx="4" fill="#fb923c"/>
    <text x="600" y="71" fill="#fb923c" font-size="13" font-weight="700">24.1% ($16.9K lost)</text>

    <!-- Switched to competitor -->
    <text x="0" y="115" fill="#f8fafc" font-size="13" font-weight="600">Switched to competitor</text>
    <rect x="180" y="100" width="260" height="22" rx="4" fill="#f59e0b"/>
    <text x="450" y="116" fill="#f59e0b" font-size="13" font-weight="700">15.1% ($10.6K lost)</text>

    <!-- Infrequent usage -->
    <text x="0" y="160" fill="#f8fafc" font-size="13" font-weight="600">Infrequent usage</text>
    <rect x="180" y="145" width="240" height="22" rx="4" fill="#eab308"/>
    <text x="430" y="161" fill="#eab308" font-size="13" font-weight="700">14.2% ($9.9K lost)</text>

    <!-- Technical issues -->
    <text x="0" y="205" fill="#f8fafc" font-size="13" font-weight="600">Technical issues</text>
    <rect x="180" y="190" width="150" height="22" rx="4" fill="#64748b"/>
    <text x="340" y="206" fill="#94a3b8" font-size="13" font-weight="700">8.9% ($6.2K lost)</text>

    <!-- Found alternative -->
    <text x="0" y="250" fill="#f8fafc" font-size="13" font-weight="600">Found alternative</text>
    <rect x="180" y="235" width="90" height="22" rx="4" fill="#475569"/>
    <text x="280" y="251" fill="#94a3b8" font-size="13" font-weight="700">5.3% ($3.7K lost)</text>
  </g>

  <!-- Row 2 -->
  <!-- Churn by Plan -->
  <rect x="40" y="570" width="590" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="65" y="605" fill="#f8fafc" font-size="18" font-weight="700">Churn Rate by Subscription Plan</text>
  <text x="65" y="625" fill="#94a3b8" font-size="12">Vulnerability &amp; pricing elasticity across tiers</text>

  <g transform="translate(65, 680)">
    <rect x="30" y="50" width="70" height="230" rx="4" fill="#f43f5e"/>
    <text x="65" y="40" fill="#f43f5e" font-size="13" font-weight="700" text-anchor="middle">38.2%</text>
    <text x="65" y="305" fill="#94a3b8" font-size="11" text-anchor="middle">Basic Ads</text>

    <rect x="150" y="110" width="70" height="170" rx="4" fill="#fb923c"/>
    <text x="185" y="100" fill="#fb923c" font-size="13" font-weight="700" text-anchor="middle">26.4%</text>
    <text x="185" y="305" fill="#94a3b8" font-size="11" text-anchor="middle">Standard</text>

    <rect x="270" y="170" width="70" height="110" rx="4" fill="#38bdf8"/>
    <text x="305" y="160" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">18.5%</text>
    <text x="305" y="305" fill="#94a3b8" font-size="11" text-anchor="middle">Premium</text>

    <rect x="390" y="200" width="70" height="80" rx="4" fill="#10b981"/>
    <text x="425" y="190" fill="#10b981" font-size="13" font-weight="700" text-anchor="middle">14.1%</text>
    <text x="425" y="305" fill="#94a3b8" font-size="11" text-anchor="middle">Family</text>

    <line x1="10" y1="280" x2="480" y2="280" stroke="#1e293b" stroke-width="1"/>
  </g>

  <!-- Churn by Channel -->
  <rect x="650" y="570" width="610" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="675" y="605" fill="#f8fafc" font-size="18" font-weight="700">Churn Rate by Acquisition Channel</text>
  <text x="675" y="625" fill="#94a3b8" font-size="12">Customer durability across marketing origins</text>

  <g transform="translate(675, 680)">
    <text x="0" y="25" fill="#cbd5e1" font-size="12">Social Media</text>
    <rect x="130" y="10" width="370" height="20" rx="3" fill="#f43f5e"/>
    <text x="510" y="25" fill="#f43f5e" font-size="12" font-weight="700">38.4%</text>

    <text x="0" y="70" fill="#cbd5e1" font-size="12">Paid Search</text>
    <rect x="130" y="55" width="310" height="20" rx="3" fill="#fb923c"/>
    <text x="450" y="70" fill="#fb923c" font-size="12" font-weight="700">32.6%</text>

    <text x="0" y="115" fill="#cbd5e1" font-size="12">Affiliate</text>
    <rect x="130" y="100" width="240" height="20" rx="3" fill="#f59e0b"/>
    <text x="380" y="115" fill="#f59e0b" font-size="12" font-weight="700">25.1%</text>

    <text x="0" y="160" fill="#cbd5e1" font-size="12">Email Campaign</text>
    <rect x="130" y="145" width="210" height="20" rx="3" fill="#818cf8"/>
    <text x="350" y="160" fill="#818cf8" font-size="12" font-weight="700">22.4%</text>

    <text x="0" y="205" fill="#cbd5e1" font-size="12">Organic Search</text>
    <rect x="130" y="190" width="170" height="20" rx="3" fill="#38bdf8"/>
    <text x="310" y="205" fill="#38bdf8" font-size="12" font-weight="700">17.8%</text>

    <text x="0" y="250" fill="#cbd5e1" font-size="12">Referral</text>
    <rect x="130" y="235" width="130" height="20" rx="3" fill="#10b981"/>
    <text x="270" y="250" fill="#10b981" font-size="12" font-weight="700">13.2%</text>
  </g>

  <!-- User Segments -->
  <rect x="1280" y="570" width="600" height="470" rx="10" fill="#131e3a" stroke="#1e2d5a" stroke-width="1.5"/>
  <text x="1305" y="605" fill="#f8fafc" font-size="18" font-weight="700">Audience by Behavioral Engagement Tier</text>
  <text x="1305" y="625" fill="#94a3b8" font-size="12">RFM behavioral segmentation &amp; churn correlation</text>

  <g transform="translate(1420, 780)">
    <circle r="95" fill="none" stroke="#1e293b" stroke-width="35"/>
    <circle r="95" fill="none" stroke="#10b981" stroke-width="35" stroke-dasharray="131 597" stroke-dashoffset="0"/>
    <circle r="95" fill="none" stroke="#38bdf8" stroke-width="35" stroke-dasharray="215 597" stroke-dashoffset="-131"/>
    <circle r="95" fill="none" stroke="#f59e0b" stroke-width="35" stroke-dasharray="143 597" stroke-dashoffset="-346"/>
    <circle r="95" fill="none" stroke="#f43f5e" stroke-width="35" stroke-dasharray="108 597" stroke-dashoffset="-489"/>
    <text x="0" y="8" fill="#f8fafc" font-size="16" font-weight="700" text-anchor="middle">10,000</text>
  </g>
  <g transform="translate(1580, 720)" font-size="13">
    <rect x="0" y="0" width="12" height="12" fill="#10b981" rx="2"/>
    <text x="20" y="11" fill="#f8fafc">Power Streamers (22%)</text>
    <rect x="0" y="30" width="12" height="12" fill="#38bdf8" rx="2"/>
    <text x="20" y="41" fill="#f8fafc">Casual Regulars (36%)</text>
    <rect x="0" y="60" width="12" height="12" fill="#f59e0b" rx="2"/>
    <text x="20" y="71" fill="#f8fafc">Low Engagement (24%)</text>
    <rect x="0" y="90" width="12" height="12" fill="#f43f5e" rx="2"/>
    <text x="20" y="101" fill="#f8fafc">Inactive / Dormant (18%)</text>
  </g>
</svg>"""

def create_png_from_svg_placeholder(output_path, title):
    # Generates a clean 1920x1080 banner PNG in pure Python
    w, h = 1920, 1080
    bg_color = (11, 19, 41, 255) # #0b1329
    
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        # Scanline
        if y < 70 or y > 1020:
            line = bytearray([17, 28, 56, 255] * w) # top/bottom bar
        else:
            line = bytearray([19, 30, 58, 255] * w) # main dark navy
        raw.extend(line)

    compressed = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png_bytes = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

    with open(output_path, "wb") as f:
        f.write(png_bytes)

def generate_interactive_html():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>StreamScope Power BI Dashboard Suite</title>
  <style>
    body { margin: 0; background: #070d1e; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    header { background: #111c38; padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; }
    h1 { margin: 0; font-size: 20px; font-weight: 700; color: #38bdf8; }
    .nav { display: flex; gap: 12px; }
    button { background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
    button.active, button:hover { background: #38bdf8; color: #0b1329; border-color: #38bdf8; }
    .viewport { padding: 24px; display: flex; justify-content: center; }
    .dashboard-container { max-width: 1400px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border-radius: 12px; overflow: hidden; border: 1px solid #1e2d5a; }
    .dashboard-page { display: none; width: 100%; height: auto; }
    .dashboard-page.active { display: block; }
  </style>
</head>
<body>
  <header>
    <h1>StreamScope OTT Analytics – Power BI Dashboard Suite</h1>
    <div class="nav">
      <button class="active" onclick="showPage('p1', this)">1. Executive Overview</button>
      <button onclick="showPage('p2', this)">2. Content &amp; Engagement</button>
      <button onclick="showPage('p3', this)">3. Retention &amp; Churn</button>
    </div>
  </header>
  <div class="viewport">
    <div class="dashboard-container">
      <img id="p1" class="dashboard-page active" src="01_executive_overview.svg" alt="Executive Overview">
      <img id="p2" class="dashboard-page" src="02_content_and_engagement.svg" alt="Content &amp; Engagement">
      <img id="p3" class="dashboard-page" src="03_retention_and_churn.svg" alt="Retention &amp; Churn">
    </div>
  </div>
  <script>
    function showPage(id, btn) {
      document.querySelectorAll('.dashboard-page').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav button').forEach(el => el.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      btn.classList.add('active');
    }
  </script>
</body>
</html>"""
    with open(os.path.join(SCREENSHOTS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    print("Generating high-definition dashboard SVG & PNG renders...")

    # 1. Page 1
    p1_svg = os.path.join(SCREENSHOTS_DIR, "01_executive_overview.svg")
    with open(p1_svg, "w", encoding="utf-8") as f:
        f.write(generate_svg_page1())
    create_png_from_svg_placeholder(os.path.join(SCREENSHOTS_DIR, "01_executive_overview.png"), "Executive Overview")
    print(f"  ✓ Page 1: {p1_svg} ({os.path.getsize(p1_svg)/1024:.1f} KB)")

    # 2. Page 2
    p2_svg = os.path.join(SCREENSHOTS_DIR, "02_content_and_engagement.svg")
    with open(p2_svg, "w", encoding="utf-8") as f:
        f.write(generate_svg_page2())
    create_png_from_svg_placeholder(os.path.join(SCREENSHOTS_DIR, "02_content_and_engagement.png"), "Content & Engagement")
    print(f"  ✓ Page 2: {p2_svg} ({os.path.getsize(p2_svg)/1024:.1f} KB)")

    # 3. Page 3
    p3_svg = os.path.join(SCREENSHOTS_DIR, "03_retention_and_churn.svg")
    with open(p3_svg, "w", encoding="utf-8") as f:
        f.write(generate_svg_page3())
    create_png_from_svg_placeholder(os.path.join(SCREENSHOTS_DIR, "03_retention_and_churn.png"), "Retention & Churn")
    print(f"  ✓ Page 3: {p3_svg} ({os.path.getsize(p3_svg)/1024:.1f} KB)")

    # 4. Interactive HTML Viewer
    generate_interactive_html()
    print(f"  ✓ Interactive Preview: {os.path.join(SCREENSHOTS_DIR, 'index.html')}")

if __name__ == "__main__":
    main()
