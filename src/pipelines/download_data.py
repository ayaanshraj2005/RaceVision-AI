import os
import urllib.request
import zipfile
import sys

# Define target paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
ZIP_URL = "https://ergast.com/downloads/f1db_csv.zip"
ZIP_PATH = os.path.join(DATA_RAW_DIR, "f1db_csv.zip")
ALT_URL = "https://github.com/rubenv/ergast-mrd/raw/master/f1db_csv.zip"

def download_file(url, target_path):
    print(f"Downloading from {url}...")
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    )
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 8
        downloaded = 0
        
        with open(target_path, 'wb') as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                f.write(buffer)
                if total_size > 0:
                    percent = int(downloaded * 100 / total_size)
                    sys.stdout.write(f"\rDownloading... {percent}% ({downloaded / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB)")
                else:
                    sys.stdout.write(f"\rDownloading... ({downloaded / 1024 / 1024:.2f} MB)")
                sys.stdout.flush()
    print("\nDownload complete!")

def download_and_extract():
    # Ensure raw directory exists
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    try:
        download_file(ZIP_URL, ZIP_PATH)
    except Exception as e:
        print(f"\nError downloading from primary URL: {e}")
        print("Attempting to use alternative community mirror...")
        try:
            download_file(ALT_URL, ZIP_PATH)
        except Exception as alt_e:
            print(f"Error downloading from mirror: {alt_e}")
            raise
            
    print("Extracting ZIP file...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_RAW_DIR)
        print(f"Extraction complete! Files extracted to {DATA_RAW_DIR}")
        
        # Clean up zip file
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)
            print("Cleaned up ZIP archive.")
    except Exception as e:
        print(f"Error during extraction: {e}")
        raise

    # Print summary of extracted files
    files = os.listdir(DATA_RAW_DIR)
    print(f"\nExtracted {len(files)} files successfully:")
    for f in sorted(files):
        size = os.path.getsize(os.path.join(DATA_RAW_DIR, f))
        print(f" - {f} ({size / 1024:.2f} KB)")

if __name__ == "__main__":
    download_and_extract()
