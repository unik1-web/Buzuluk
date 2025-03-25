import pandas as pd
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime
import requests
import time
import os
import socket
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"

def check_server_availability(host, port, timeout=5):
    try:
        logging.info(f"Attempting to connect to {host}:{port}")
        socket.create_connection((host, port), timeout=timeout)
        logging.info("Connection successful")
        return True
    except socket.timeout:
        logging.error("Connection timed out")
        return False
    except ConnectionRefusedError:
        logging.error("Connection refused - port might be closed")
        return False
    except Exception as e:
        logging.error(f"Connection error: {str(e)}")
        return False

def find_next_cell_value(cell):
    """Find the value in the cell below the current cell"""
    try:
        # Get parent row
        current_row = cell.find_parent('tr')
        if not current_row:
            return None
            
        # Get all rows in the table
        table = current_row.find_parent('table')
        if not table:
            return None
            
        rows = table.find_all('tr')
        
        # Find current row index
        current_index = rows.index(current_row)
        
        # Get next row if it exists
        if current_index + 1 < len(rows):
            next_row = rows[current_index + 1]
            # Find cell at the same position
            cells = next_row.find_all('td')
            current_cell_index = current_row.find_all('td').index(cell)
            if current_cell_index < len(cells):
                value = cells[current_cell_index].text.strip()
                # Remove 'т' if present and convert to float
                value = value.replace('т', '').strip()
                if re.match(r'^\d+\.?\d*$', value):
                    return float(value)
    except Exception as e:
        logging.error(f"Error finding next cell value: {str(e)}")
    return None

def extract_data_from_website(url, last_processed_time=None):
    try:
        # Get the webpage content with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all cells with green background (checking different ways)
        green_cells = []
        
        # Method 1: Background color in style
        cells_style = soup.find_all('td', style=lambda x: x and any(color in x.lower() for color in [
            'background-color: green',
            'background: green',
            'background-color:#00ff00',
            'background:#00ff00',
            'background-color:lime',
            'background:lime'
        ]))
        green_cells.extend(cells_style)
        
        # Method 2: Class-based styling
        cells_class = soup.find_all('td', class_=lambda x: x and ('green' in str(x).lower()))
        green_cells.extend(cells_class)
        
        # Remove duplicates
        green_cells = list(set(green_cells))
        
        release_data = []
        current_time = datetime.now()
        
        for cell in green_cells:
            if 'Выпуск' in cell.text:
                # Get the value from the cell below
                tonnage = find_next_cell_value(cell)
                if tonnage is not None:
                    # Get the header row to determine which furnace
                    table = cell.find_parent('table')
                    if table:
                        header = table.find('tr')
                        if header:
                            header_text = header.text.strip()
                            furnace = 'Печь-2' if 'ПЕЧЬ-2' in header_text.upper() else 'Печь-1'
                            
                            # Create timestamp string
                            timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Only process if we haven't seen this timestamp before
                            if last_processed_time is None or current_time > last_processed_time:
                                release_data.append({
                                    'timestamp': timestamp,
                                    'tonnage': tonnage,
                                    'furnace': furnace
                                })
                                logging.info(f"Found new release: {furnace} - {tonnage}т")
        
        # Convert to DataFrame
        df = pd.DataFrame(release_data)
        
        # Save to CSV
        if not df.empty:
            try:
                file_exists = os.path.exists('release_data.csv')
                df.to_csv('release_data.csv', mode='a', header=not file_exists, index=False)
                logging.info(f"Successfully saved {len(df)} records to release_data.csv")
            except Exception as e:
                logging.error(f"Error saving to CSV: {str(e)}")
        
        return df, current_time if not df.empty else last_processed_time
        
    except Exception as e:
        logging.error(f"Error processing website: {str(e)}")
        return pd.DataFrame(), last_processed_time

def monitor_website(url, interval=5):
    """
    Continuously monitor the website at specified intervals
    """
    logging.info(f"Starting website monitoring at {url}")
    logging.info(f"Current working directory: {os.getcwd()}")
    
    last_processed_time = None
    
    while True:
        try:
            df, last_processed_time = extract_data_from_website(url, last_processed_time)
            if not df.empty:
                print("\nExtracted Data:")
                print(df)
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            break
        except Exception as e:
            logging.error(f"Error during monitoring: {str(e)}")
            time.sleep(interval)

if __name__ == "__main__":
    url = "http://172.26.8.200:81/all_dsp_mnlz_index.php"
    monitor_website(url, interval=5)  # Check every 5 seconds
