import email
import mailbox
import regex as re
import csv
import time
from datetime import datetime
import threading
from queue import Queue

def process_message_with_timeout(message, timeout=1):
    """Process a single message in a separate thread with timeout"""
    result_queue = Queue()
    
    def process():
        try:
            if message.is_multipart():
                body = ''
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            result_queue.put(("success", body))
        except Exception as e:
            result_queue.put(("error", str(e)))
    
    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        print("Timeout: Thread exceeded timeout and was terminated")
        return "timeout", "Message processing timed out"
    
    if not result_queue.empty():
        return result_queue.get()
    return "error", "Unknown error occurred"

def extract_emails_from_thunderbird(mbox_path, output_file):
    print(f"Opening mailbox at: {mbox_path}")
    
    try:
        mbox = mailbox.mbox(mbox_path)
        print(f"Mailbox opened successfully. Starting to process messages...")
    except Exception as e:
        print(f"Error opening mailbox: {e}")
        return 0
        
    extracted_data = []
    message_count = 0
    skipped_messages = []


    cmd_pattern = re.compile(r'COMMAND LINE ARGUMENTS:\s*\n(?:[^"\n]*"[^"]*"\s*)*"([^"]+)"\s*"([^"]+@[^"]+)"\s*(?:"[^"]*"\s*)*')
    
    for message in mbox:
        message_count += 1
        try:
            print(f"Processing message {message_count}...")
            
            # Check for large messages
            if len(message.as_bytes()) > 10 * 1024 * 1024:  # 10 MB limit
                print(f"Skipping message {message_count}: too large")
                skipped_messages.append(message_count)
                continue
            
            # Process the message with a timeout
            status, body = process_message_with_timeout(message)
            
            if status != "success":
                print(f"Message {message_count} - {status}: {body}")
                skipped_messages.append(message_count)
                continue
            
            # Log progress if command-line arguments are found
            if 'COMMAND LINE ARGUMENTS' in body:
                print(f"Found command line arguments in message {message_count}")
            
            # Regex search for email data
            match = cmd_pattern.search(body)
            if match:
                name = match.group(1)
                email_address = match.group(2)
                print(f"Found email: {email_address}")
                
                # Extract additional information
                subject = message.get('subject', '')
                order_number = None
                order_match = re.search(r'bestelling (\d+)', subject, re.IGNORECASE)
                if order_match:
                    order_number = order_match.group(1)
                
                # Append the extracted data
                extracted_data.append({
                    'date': message.get('date', ''),
                    'order_number': order_number,
                    'name': name,
                    'email': email_address,
                    'message_number': message_count
                })
        
        except Exception as e:
            print(f"Error processing message {message_count}: {e}")
            skipped_messages.append(message_count)
            continue
    
    # Summary of results
    print(f"\nProcessing complete:")
    print(f"- Processed messages: {message_count}")
    print(f"- Extracted emails: {len(extracted_data)}")
    print(f"- Skipped messages: {len(skipped_messages)}")
    if skipped_messages:
        print(f"- Skipped message numbers: {skipped_messages}")
    
    # Write results to a CSV file
    print(f"\nWriting results to {output_file}")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'order_number', 'name', 'email', 'message_number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in extracted_data:
            writer.writerow(data)
    
    # Write skipped messages to a separate file
    skip_file = output_file.replace('.csv', '_skipped.txt')
    with open(skip_file, 'w') as f:
        f.write(f"Skipped messages ({len(skipped_messages)}):\n")
        f.write('\n'.join(map(str, skipped_messages)))
    
    return len(extracted_data)

if __name__ == "__main__":
    mbox_path = r"c:\Users\SiebeBosch\AppData\Roaming\Thunderbird\Profiles\zqb5p1u6.default-release\ImapMail\imap.strato.com\INBOX"
    output_file = f"extracted_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    start_time = time.time()
    count = extract_emails_from_thunderbird(mbox_path, output_file)
    end_time = time.time()
    
    print(f"\nExtraction completed in {end_time - start_time:.2f} seconds")
