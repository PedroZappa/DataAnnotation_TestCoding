import requests
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

def decode_secret_message(google_doc_url):
    """
    Reads a public Google Doc, parses character coordinates, 
    and prints a grid revealing the secret message. 
    """
    
    # Convert the publish URL to export format for easier parsing
    # if '/pub' in google_doc_url:
    #     export_url = google_doc_url.replace('/pub', '/export?format=html')
    # else:
    #     export_url = google_doc_url + '/export?format=html'
    export_url = prepare_export_url(google_doc_url)
    
    try:
        # Download the document as HTML
        response = requests.get(export_url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the table containing the coordinates and characters
        table = soup.find('table')
        if not table:
            print("No table found in the document")
            return
        # Parse the table data
        coordinates = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows: # Parse the table
            cells = row.find_all('td')
            if len(cells) >= 3:
                try:
                    x = int(cells[0].get_text().strip())
                    character = cells[1].get_text().strip()
                    y = int(cells[2].get_text().strip())
                    coordinates.append((x, y, character))
                except ValueError:
                    continue
        
        # Create and populate the grid
        if coordinates:
            create_and_print_grid(coordinates)
        else:
            print("No valid coordinate data found")
            
    except requests.RequestException as e:
        print(f"Error fetching document: {e}")
    except Exception as e:
        print(f"Error processing document: {e}")

def prepare_export_url(input_url):
    """
    Converts a Google Doc URL to an export URL.
    """
    parsed_url = urlparse(input_url)
    path_segs = parsed_url.path.split('/')
    
    try:
        d_index = path_segs.index('d')
        doc_id = path_segs[d_index + 1]
    except (ValueError, IndexError):
        return input_url  # Fallback for invalid URLs
    
    new_path = f'/document/d/{doc_id}/export'
    new_url = urlunparse(( # Reconstruct the URL
        parsed_url.scheme,
        parsed_url.netloc,
        new_path,
        '',
        'format=html',
        ''
    ))
    return new_url

def create_and_print_grid(coordinates):
    """
    Creates a 2D grid from coordinate data and prints it.
    """
    if not coordinates:
        return
    
    # Get dimensions needed
    max_x = max(coord[0] for coord in coordinates)
    max_y = max(coord[1] for coord in coordinates)
    
    # Create grid filled with spaces
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # Place characters in the grid
    for x, y, character in coordinates:
        if character:  # Only place non-empty characters
            grid[y][x] = character
    
    # Print the grid
    for row in grid:
        print(''.join(row))


# Run
if __name__ == "__main__":
    google_doc_url = "https://docs.google.com/document/d/1qsD4zdqKcZT4UAuOQIW2nJZigKDWNOiMMNoi-5Zwgz4"
    decode_secret_message(google_doc_url)
