import json
import os
import requests

def fetch_html(site_name, url, output_dir="site_html"):
    """Fetches the HTML content of a given URL and saves it to a file."""
    try:
        print(f"Fetching HTML for {site_name}...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        html_content = response.text
        
        # Save HTML to file
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{site_name}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
        
        print(f"HTML for {site_name} saved to {file_path}")

    except requests.RequestException as e:
        print(f"Error fetching {site_name}: {e}")

def main():
    json_file = "src/topics/technologie.json"
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {json_file} not found!")
        return

    for category, details in data.items():
        print(f"Processing category: {category}")
        sources = details.get("sources", {})
        for site_name, url in sources.items():
            fetch_html(site_name, url)

if __name__ == "__main__":
    main()
