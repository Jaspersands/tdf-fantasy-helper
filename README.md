# Tour de France (TdF) Fantasy Helper

A high-performance, premium client-side recreation of the Tour de France Fantasy Helper website. This application runs entirely in your browser without external server-side database requirements. It loads race data dynamically from `riders_data.json` and performs all filtering, sorting, comparisons, fantasy squad rule validations, and analytics directly on the client.

## Core Features
1. **Riders Database**: View, search, filter, and sort riders for Tour de France 2026, Tour de France 2025, and Vuelta 2025. Supports Cards vs. Table layouts.
2. **Rider Comparison**: Select up to 5 riders to compare side-by-side across team, categories, points, wins, value credits, ranks, and nationalities.
3. **Interactive Team Builder**: Assemble a squad of up to 8 riders. The app automatically checks and enforces official category restrictions (Leaders <= 3, Climbers <= 3, Sprinters <= 3, All-rounders <= 5), budget constraints (max 120 credits), and team allocations (max 3 from same team).
4. **Canvas Squad Exporter**: Click a button to draw your fantasy squad onto an HTML5 Canvas and download it instantly as a beautiful PNG image to share.
5. **Real-time Analytics**: Displays category breakdown statistics and renders interactive price/value distribution graphs using Chart.js.

---

## Getting Started

### 1. Launching the App
The app is built using HTML, CSS, and Vanilla JavaScript. You can open any `.html` file (e.g. `index.html`) directly in a web browser, but it is highly recommended to run a simple local web server to enable smooth local storage and assets handling:

1. Open your terminal.
2. Navigate to this directory:
   ```bash
   cd "/Users/jaspersands/Desktop/tdf fantasy"
   ```
3. Start a built-in Python web server:
   ```bash
   python3 -m http.server 8000
   ```
4. Open [http://localhost:8000](http://localhost:8000) in your web browser.

---

## Daily Data Updates

During the Tour de France, statistics and rider points change daily after each stage. To keep your local website fully updated, a scraper script `update_data.py` is included.

### 1. Manual Update
To pull the latest points and ranks immediately:
```bash
python3 "/Users/jaspersands/Desktop/tdf fantasy/update_data.py"
```
This script downloads the updated values and rewrites `riders_data.json` in place. Refresh your browser to see the latest stats.

### 2. Automatic Daily Updates (macOS Cron)
You can automate this update to run every evening (e.g., at 6:00 PM when TdF stages typically finish) using the macOS built-in cron scheduler:

1. Open Terminal.
2. Open the crontab editor by running:
   ```bash
   crontab -e
   ```
3. Press `i` to enter insert mode in vi/vim.
4. Copy and paste the following line (make sure the path to Python and your project folder is correct):
   ```cron
   0 18 * * * /usr/bin/python3 "/Users/jaspersands/Desktop/tdf fantasy/update_data.py" > /tmp/tdf_update.log 2>&1
   ```
5. Press `Esc` and type `:wq` then press `Enter` to save and exit.
6. The script will now run automatically in the background at 18:00 (6:00 PM) every single day, keeping your fantasy helper updated throughout the tour.
