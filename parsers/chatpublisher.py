# Configure your paths here
INPUT_FILE = r"c:\SYNC\ADMINISTRATIE\PRIVE\Uitbouw\Ingebrekestelling\_chat_siebe_jay.txt"    # Replace with your input file path
OUTPUT_FILE = "siebe_jay.qmd"    # Replace with your desired output file path

import re
import os
from datetime import datetime

def parse_whatsapp_chat(input_file, output_file):
    """
    Parse WhatsApp chat history and convert it to Quarto markdown format.
    """
    # Updated regular expression for matching WhatsApp messages
    # Matches: [DD-MM-YYYY, HH:mm:ss] Name: Message
    message_pattern = r'^\[(\d{2}-\d{2}-\d{4}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)$'
    
    # Updated regular expression for matching media files
    media_pattern = r'<bijgevoegd:\s*([^>]+)>'
    
    current_date = None
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        # Write initial header
        outfile.write("---\ntitle: WhatsApp Chat History\nformat: html\n---\n\n")
        
        for line in infile:
            # Remove any invisible characters
            line = line.strip().replace('\u200e', '')
            if not line:
                continue
                
            match = re.match(message_pattern, line)
            if match:
                date_str, time, writer, message = match.groups()
                
                # Convert date string to datetime object
                try:
                    date = datetime.strptime(date_str, '%d-%m-%Y')
                except ValueError:
                    print(f"Warning: Could not parse date: {date_str}")
                    continue
                
                # Write date header if it's a new date
                formatted_date = date.strftime('%B %d, %Y')
                if formatted_date != current_date:
                    current_date = formatted_date
                    outfile.write(f"\n## {formatted_date}\n\n")
                
                # Process message content for media files
                processed_message = message
                media_match = re.search(media_pattern, message)
                if media_match:
                    media_file = media_match.group(1)
                    # Replace media attachment with markdown image link
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        processed_message = f"\n\n![{media_file}](img/{media_file}){{width=50% fig-align='left'}}"
                    elif media_file.lower().endswith('.opus'):
                        # Audio files
                        processed_message = f"\n\n::: {{.column-margin}}\n<audio controls>\n  <source src='img/{media_file}' type='audio/ogg; codecs=opus'>\n  Your browser does not support the audio element.\n</audio>\n:::"
                    elif media_file.lower().endswith('.mp4'):
                        # Video files
                        processed_message = f"\n\n::: {{.column-margin}}\n<video controls width='100%'>\n  <source src='img/{media_file}' type='video/mp4'>\n  Your browser does not support the video element.\n</video>\n:::"
                    else:
                        # For non-image files (like videos), create a regular link
                        processed_message = f"\n\n![{media_file}](img/{media_file}){{width=50% fig-align='left'}}"
                
                # Write the message with an extra newline after each message
                outfile.write(f"[{time}] {writer}: {processed_message}\n\n")
            else:
                # Handle continuation lines (messages that span multiple lines)
                if line and current_date:  # Only write if we've seen at least one valid message
                    outfile.write(f"{line}\n\n")

def main():
    """
    Main function to run the conversion
    """
    # Ensure output file has .qmd extension
    output_file = OUTPUT_FILE if OUTPUT_FILE.endswith('.qmd') else OUTPUT_FILE + '.qmd'
    
    try:
        parse_whatsapp_chat(INPUT_FILE, output_file)
        print(f"Conversion complete. Output written to {output_file}")
    except FileNotFoundError:
        print(f"Error: Could not find input file '{INPUT_FILE}'")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == '__main__':
    main()