# Configure your paths here
INPUT_FILE = r"c:\SYNC\ADMINISTRATIE\PRIVE\Uitbouw\Documentatie\chatgeschiedenis\_chat_siebe_jay.txt"    # Replace with your input file path
OUTPUT_FILE = r"c:\SYNC\ADMINISTRATIE\PRIVE\Uitbouw\Documentatie\chatgeschiedenis\siebe_jay.qmd"    # Replace with your desired output file path
MEDIA_FOLDER = r"c:\SYNC\ADMINISTRATIE\PRIVE\Uitbouw\Documentatie\chatgeschiedenis\img"    # Replace with your input file path

import re
import os
from datetime import datetime
import whisper
from pathlib import Path

def transcribe_audio(audio_path, model="base"):
    """
    Transcribe an audio file using Whisper.
    Returns the transcribed text in the detected language.
    """
    try:
        # Load the Whisper model
        whisper_model = whisper.load_model(model)
        
        # Transcribe the audio
        result = whisper_model.transcribe(str(audio_path))
        
        return result["text"]
    except Exception as e:
        print(f"Error transcribing {audio_path}: {str(e)}")
        return None

def parse_whatsapp_chat(input_file, output_file):
    """
    Parse WhatsApp chat history and convert it to Quarto markdown format.
    Includes audio transcription for .opus files.
    """
    # Updated regular expression for matching WhatsApp messages
    message_pattern = r'^\[(\d{2}-\d{2}-\d{4}),\s*(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)$'
    
    # Updated regular expression for matching media files
    media_pattern = r'<bijgevoegd:\s*([^>]+)>'
    
    current_date = None
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        

        # Write initial header with adjusted column layout setup
        outfile.write("""---
title: WhatsApp Chat History
format: 
    html:
        css: styles.css
        page-layout: article
        margin-left: 2em
        margin-right: 2em
---

""")
                
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
                # Process regular messages differently than media messages
                if media_match:
                    media_file = media_match.group(1)
                    media_abs_path = Path(MEDIA_FOLDER) / media_file

                    # Handle different media types
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        processed_message = f"\n\n![{media_file}](img/{media_file}){{width=50% fig-align='left'}}\n"

                    elif media_file.lower().endswith('.opus'):
                        print("searching audio file: ", media_abs_path)
                        if media_abs_path.exists():
                            transcription = transcribe_audio(media_abs_path)
                            if transcription:
                                processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n <audio controls width='100%'><source src='img/{media_file}' type='audio/ogg; codecs=opus'>Your browser does not support the audio element.</audio>\n:::\n::: {{.g-col-8}}\n*{transcription}*\n:::\n:::\n"
                            else:
                                processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n <audio controls width='100%'><source src='img/{media_file}' type='audio/ogg; codecs=opus'>Your browser does not support the audio element.</audio>\n:::\n::: {{.g-col-8}}\n*[Transcription failed]*\n:::\n:::\n"
                        else:
                            processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n*[Audio file not found]*\n:::\n::: {{.g-col-8}}\n*[Audio file not found]*\n:::\n:::\n"

                    elif media_file.lower().endswith('.mp4'):
                        print("searching video file: ", media_abs_path)
                        if media_abs_path.exists():
                            transcription = transcribe_audio(media_abs_path)
                            if transcription:
                                processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n <video controls width='100%'><source src='img/{media_file}' type='video/mp4'>Your browser does not support the video element.</video>\n:::\n::: {{.g-col-8}}\n*{transcription}*\n:::\n:::\n"
                            else:
                                processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n <video controls width='100%'><source src='img/{media_file}' type='video/mp4'>Your browser does not support the video element.</video>\n:::\n::: {{.g-col-8}}\n*[Transcription failed]*\n:::\n:::\n"
                        else:
                            processed_message = f"::: {{.grid}}\n::: {{.g-col-4}}\n{media_file}\n:::\n::: {{.g-col-8}}\n*[Video file not found]*\n:::\n:::\n"
                    else:
                        processed_message = f"{media_file}"
                else:
                    # For regular text messages, ensure they're on their own line
                    processed_message = f"{message}"

                # Write the message with proper spacing
                outfile.write(f"\n[{time}] {writer}:")  # Message header with newline before
                if media_match:
                    outfile.write("\n\n")  # Extra space for media content
                else:
                    outfile.write(f" {processed_message}")  # Regular messages inline after timestamp
                outfile.write(processed_message if media_match else "\n\n")  # Media content or closing newlines

            else:
                # Handle continuation lines with proper spacing
                if line and current_date:
                    outfile.write(f"\n{line}\n\n")
def main():
    """
    Main function to run the conversion
    """
    # Ensure output file has .qmd extension
    output_file = OUTPUT_FILE if OUTPUT_FILE.endswith('.qmd') else OUTPUT_FILE + '.qmd'
    
    try:
        # Ensure the img directory exists
        Path("img").mkdir(exist_ok=True)
        
        parse_whatsapp_chat(INPUT_FILE, output_file)
        print(f"Conversion complete. Output written to {output_file}")
    except FileNotFoundError:
        print(f"Error: Could not find input file '{INPUT_FILE}'")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == '__main__':
    main()