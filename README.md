# Tour de France (TdF) Fantasy Helper

A high-performance, premium client-side recreation of the Tour de France Fantasy Helper website. This application runs entirely in your browser without external server-side database requirements. It loads race data dynamically from `riders_data.json` and performs all filtering, sorting, comparisons, fantasy squad rule validations, and analytics directly on the client.

## Core Features
1. **Riders Database**: View, search, filter, and sort riders for Tour de France 2026, Tour de France 2025, and Vuelta 2025. Supports Cards vs. Table layouts.
2. **Rider Comparison**: Select up to 5 riders to compare side-by-side across team, categories, points, wins, value credits, ranks, and nationalities.
3. **Interactive Team Builder**: Assemble a squad of up to 8 riders. The app automatically checks and enforces official category restrictions (Leaders <= 3, Climbers <= 3, Sprinters <= 3, All-rounders <= 5), budget constraints (max 120 credits), and team allocations (max 3 from same team).
4. **Canvas Squad Exporter**: Click a button to draw your fantasy squad onto an HTML5 Canvas and download it instantly as a beautiful PNG image to share.
5. **Real-time Analytics**: Displays category breakdown statistics and renders interactive price/value distribution graphs using Chart.js.

---

## Getting Started & Automatic Updates

The app includes a local server (`server.py`) that serves the website and **automatically updates the riders and stages databases** in the background when you visit the site (rate-limited to once every 15 minutes to prevent spamming).

1. Open your terminal.
2. Start the local server:
   ```bash
   python3 "/Users/jaspersands/Desktop/tdf fantasy/server.py"
   ```
3. Open **[http://localhost:8005](http://localhost:8005)** in your web browser.

No manual updates or cron jobs are necessary! Whenever you open the site, it will check if the database is older than 15 minutes and fetch the latest stage classifications, points, and withdrawals automatically in the background.

## Manual Database Updates
If you ever want to force a database refresh manually:
```bash
python3 "/Users/jaspersands/Desktop/tdf fantasy/update_data.py"
```
This will rebuild `riders_data.json` and `stages_data.json` immediately.

