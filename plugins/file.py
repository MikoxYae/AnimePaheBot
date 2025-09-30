#..........This Bot Made By [RAHAT](https://t.me/r4h4t_69)..........#
#..........Anyone Can Modify This As He Likes..........#
#..........Just one requests do not remove my credit..........#

import requests
import os
import string
import random
import shutil
import re
from helper.database import*
import subprocess
import json
from config import LOG_CHANNEL
import cloudscraper
import time
import math

def create_short_name(name):
    # Check if the name length is greater than 25
    if len(name) > 30:
        # Extract all capital letters from the name
        short_name = ''.join(word[0].upper() for word in name.split())					
        return short_name    
    return name

def get_media_details(path):
    try:
        # Run ffprobe command to get media info in JSON format
        result = subprocess.run(
            [
                "ffprobe",
                "-hide_banner",
                "-loglevel",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Error: Unable to process the file. FFprobe output:\n{result.stderr}")
            return None

        # Parse JSON output
        media_info = json.loads(result.stdout)

        # Extract width, height, and duration
        video_stream = next((stream for stream in media_info["streams"] if stream["codec_type"] == "video"), None)
        width = video_stream.get("width") if video_stream else None
        height = video_stream.get("height") if video_stream else None
        duration = media_info["format"].get("duration")

        return width, height, duration

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def time_formatter(seconds):
    """Convert seconds to human readable time format"""
    if seconds is None:
        return "Unknown"
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def download_file(url, download_path, progress_message=None, anime_name=None, episode_number=None):
    """Download file with progress bar and retry logic"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://kwik.cx/',
        'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
        'Connection': 'keep-alive',
    }
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Use regular requests for faster download
            with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                r.raise_for_status()
                
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                last_update_time = start_time
                chunk_size = 1024 * 1024  # 1MB chunks for faster download
                
                with open(download_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Update progress every 2 seconds
                            current_time = time.time()
                            if progress_message and (current_time - last_update_time) >= 2:
                                last_update_time = current_time
                                
                                # Calculate progress
                                percentage = (downloaded / total_size) * 100 if total_size > 0 else 0
                                elapsed_time = current_time - start_time
                                speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                # Create progress bar
                                filled_length = int(10 * downloaded // total_size) if total_size > 0 else 0
                                bar = '█' * filled_length + '░' * (10 - filled_length)
                                
                                # Format progress message
                                progress_text = f"<b>📥 Downloading...</b>\n\n"
                                progress_text += f"<b>Anime:</b> <code>{anime_name or 'Unknown'}</code>\n"
                                progress_text += f"<b>Episode:</b> <code>{episode_number or 'Unknown'}</code>\n\n"
                                progress_text += f"<code>{bar}</code> {percentage:.1f}%\n\n"
                                progress_text += f"<b>Downloaded:</b> {humanbytes(downloaded)} / {humanbytes(total_size)}\n"
                                progress_text += f"<b>Speed:</b> {humanbytes(speed)}/s\n"
                                progress_text += f"<b>ETA:</b> {time_formatter(eta)}"
                                
                                try:
                                    progress_message.edit(progress_text)
                                except:
                                    pass
            
            # If download completed successfully, break the retry loop
            return download_path
            
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, requests.exceptions.IncompleteRead) as e:
            retry_count += 1
            if retry_count < max_retries:
                if progress_message:
                    try:
                        progress_message.edit(f"<b>⚠️ Connection interrupted. Retrying... ({retry_count}/{max_retries})</b>")
                    except:
                        pass
                time.sleep(2)  # Wait before retry
            else:
                # Try with cloudscraper as final fallback
                try:
                    scraper = cloudscraper.create_scraper()
                    with scraper.get(url, headers=headers, stream=True) as r:
                        r.raise_for_status()
                        
                        total_size = int(r.headers.get('content-length', 0))
                        downloaded = 0
                        start_time = time.time()
                        last_update_time = start_time
                        chunk_size = 1024 * 1024
                        
                        with open(download_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    
                                    # Update progress every 2 seconds
                                    current_time = time.time()
                                    if progress_message and (current_time - last_update_time) >= 2:
                                        last_update_time = current_time
                                        
                                        # Calculate progress
                                        percentage = (downloaded / total_size) * 100 if total_size > 0 else 0
                                        elapsed_time = current_time - start_time
                                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                                        eta = (total_size - downloaded) / speed if speed > 0 else 0
                                        
                                        # Create progress bar
                                        filled_length = int(10 * downloaded // total_size) if total_size > 0 else 0
                                        bar = '█' * filled_length + '░' * (10 - filled_length)
                                        
                                        # Format progress message
                                        progress_text = f"<b>📥 Downloading... (Fallback mode)</b>\n\n"
                                        progress_text += f"<b>Anime:</b> <code>{anime_name or 'Unknown'}</code>\n"
                                        progress_text += f"<b>Episode:</b> <code>{episode_number or 'Unknown'}</code>\n\n"
                                        progress_text += f"<code>{bar}</code> {percentage:.1f}%\n\n"
                                        progress_text += f"<b>Downloaded:</b> {humanbytes(downloaded)} / {humanbytes(total_size)}\n"
                                        progress_text += f"<b>Speed:</b> {humanbytes(speed)}/s\n"
                                        progress_text += f"<b>ETA:</b> {time_formatter(eta)}"
                                        
                                        try:
                                            progress_message.edit(progress_text)
                                        except:
                                            pass
                    return download_path
                except Exception as fallback_error:
                    raise Exception(f"Download failed after {max_retries} retries: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Download error: {str(e)}")
    
    return download_path

def sanitize_filename(file_name):
    # Remove invalid characters from the file name
    file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
    return file_name

def send_and_delete_file(client, chat_id, file_path, thumbnail=None, caption="", user_id=None, progress_message=None, anime_name=None, episode_number=None):
    upload_method = get_upload_method(user_id)  # Retrieve user's upload method
    forwarding_channel = LOG_CHANNEL  # Channel to forward the file

    # Progress callback for upload
    def progress_callback(current, total):
        try:
            if progress_message:
                percentage = (current / total) * 100 if total > 0 else 0
                filled_length = int(10 * current // total) if total > 0 else 0
                bar = '█' * filled_length + '░' * (10 - filled_length)
                
                progress_text = f"<b>📤 Uploading...</b>\n\n"
                progress_text += f"<b>Anime:</b> <code>{anime_name or 'Unknown'}</code>\n"
                progress_text += f"<b>Episode:</b> <code>{episode_number or 'Unknown'}</code>\n\n"
                progress_text += f"<code>{bar}</code> {percentage:.1f}%\n\n"
                progress_text += f"<b>Uploaded:</b> {humanbytes(current)} / {humanbytes(total)}"
                
                progress_message.edit(progress_text)
        except:
            pass

    try:        
        user_info = client.get_users(user_id)
        user_details = f"Downloaded by: @{user_info.username if user_info.username else 'Unknown'} (ID: {user_id})"
        
        # Add user info to the caption
        caption_with_info = f"{caption}\n\n{user_details}"
        
        if upload_method == "document":
            # Send as document
            sent_message = client.send_document(
                chat_id,
                file_path,
                thumb=thumbnail if thumbnail else None,
                caption=caption,
                progress=progress_callback
            )
        else:
            # Send as video
            details = get_media_details(file_path)
            if details:
                width, height, duration = details  # Unpack the values properly
                width = int(width) if width else None
                height = int(height) if height else None
                duration = int(float(duration)) if duration else None
            sent_message = client.send_video(
                chat_id,
                file_path,
                duration= duration if duration else None,
                width= width if width else None,
                height= height if height else None,
                supports_streaming= True,
                has_spoiler= True,
                thumb=None,
                caption=caption,
                progress=progress_callback
            )
        
        # Forward the message to the specified channel (with error handling)
        try:
            forward_message = client.copy_message(
                chat_id=forwarding_channel,
                from_chat_id=chat_id,
                message_id=sent_message.id,
                caption=caption_with_info
            )
        except Exception as e:
            print(f"Failed to forward to LOG_CHANNEL: {e}")
            # Continue even if forwarding fails
        
        # Delete the file after sending
        os.remove(file_path)
        
    except Exception as e:
        client.send_message(chat_id, f"Error: {str(e)}")
        

def remove_directory(directory_path):
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory '{directory_path}' does not exist.")
    
    try:
        shutil.rmtree(directory_path)
        #print(f"Directory '{directory_path}' has been removed successfully.")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except Exception as e:
        print(f"An error occurred while removing the directory: {e}")

def random_string(length):
    if length < 1:
        raise ValueError("Length must be a positive integer.")
    
    # Define the characters to choose from (letters and digits)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
