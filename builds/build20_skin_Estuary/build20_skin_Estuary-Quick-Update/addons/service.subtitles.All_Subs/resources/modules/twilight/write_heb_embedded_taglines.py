import requests,base64
from resources.modules import log


def write(video_tagline_to_write):

    try:
        # AC
        ac_url = "https://pastebin.com/raw/7WnhSzeE"
        ac = requests.get(ac_url).text
        
        # Fetch existing content and SHA
        taglines_file_url = "https://api.github.com/repos/DarkSubsHebSubs/DarkSubsHebSubs/contents/taglines.txt"
        response = requests.get(taglines_file_url, headers={"Authorization": f"Bearer {ac}"})
        data = response.json()
        
        # Fetch existing content and decode it
        decoded_content = base64.b64decode(data["content"]).decode("utf-8")
        
        # Clean up existing taglines
        current_taglines = [line.strip() for line in decoded_content.split("\n")]
        
        if video_tagline_to_write not in current_taglines:
        
            # Add new tagline to current taglines
            updated_taglines = "\n".join(current_taglines + [video_tagline_to_write])

            # Encode new content
            encoded_content = base64.b64encode(updated_taglines.encode("utf-8")).decode("utf-8")

            # Create commit data
            commit_data = {
                "message": f"{video_tagline_to_write}",
                "content": encoded_content,
                "sha": data["sha"]
            }

            # Send PUT request to update the file
            put_response = requests.put(taglines_file_url, json=commit_data, headers={"Authorization": f"Bearer {ac}"})

            if put_response.status_code == 200:
                log.warning(f"WRITE | Added {video_tagline_to_write} to taglines list.")
            else:
                error_message = put_response.json().get("message", "Unknown error")
                log.warning(f"WRITE | Failed to update the file. Reason: {error_message}")
                
        else:
            log.warning(f"WRITE | Skipping - {video_tagline_to_write} already exists in current_taglines.")
    
    except Exception as e:
        log.warning(f"WRITE | Exception: {str(e)}")
        pass