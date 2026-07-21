import http.server
import socketserver
import os
import time
import threading
import sys

PORT = 8005
DIRECTORY = os.path.dirname(os.path.realpath(__file__))

class AutoUpdateHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Trigger update when accessing entry pages
        path = self.path.split('?')[0]
        if path in ['', '/', '/index.html', '/optimizer.html', '/team-builder.html']:
            self.trigger_background_update()
            
        return super().do_GET()

    def trigger_background_update(self):
        db_path = os.path.join(DIRECTORY, "riders_data.json")
        now = time.time()
        
        # Check if update is already running
        if hasattr(self.__class__, '_updating') and self.__class__._updating:
            return
            
        should_update = False
        if not os.path.exists(db_path):
            should_update = True
        else:
            mtime = os.path.getmtime(db_path)
            # If the file hasn't been modified in 15 minutes, trigger update
            if now - mtime > 900: 
                should_update = True

        if should_update:
            self.__class__._updating = True
            print("Database is older than 15 minutes. Starting background data update...")
            thread = threading.Thread(target=self.run_scraper)
            thread.daemon = True
            thread.start()

    def run_scraper(self):
        try:
            # Add current directory to path in case it's not present
            if DIRECTORY not in sys.path:
                sys.path.insert(0, DIRECTORY)
            
            # Import and run update_data's main
            import update_data
            update_data.main()
            print("Background data update completed successfully.")
        except Exception as e:
            print(f"Error in background data update: {e}")
        finally:
            self.__class__._updating = False

# Class variable to track running update
AutoUpdateHTTPRequestHandler._updating = False

def main():
    # Change working directory to script directory
    os.chdir(DIRECTORY)
    
    # Allow address reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), AutoUpdateHTTPRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print("Scraper will run automatically in the background when you visit the website.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
