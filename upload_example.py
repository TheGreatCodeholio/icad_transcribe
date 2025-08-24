import requests

def post_audio():
    # URL of your Flask endpoint
    url = "https://stt.icaddispatch.com/api/transcribe/get"

    # Path to the audio file on your local system
    audio_file_path = "/srv/dev_projects/personal/IdeaProjects/icad_dispatch/test_audio/station_79_voice.mp3"

    # Form fields that you want to match your Flask endpoint
    # The keys here (audioName, audioType, dateTime, etc.)
    # should match the form fields your endpoint expects.
    data = {
        "key": "6aa4f142-3851-452e-a140-8fa7450aa49f",
        "transcribe_config_id": 1,
        "sources": "[]"
    }

    # The 'files' dict is used to send multipart/form-data for the file upload.
    # The key should match the field name in request.files.get('audioFile')
    files = {
        "audio": open(audio_file_path, "rb")
    }

    # Send the POST request
    response = requests.post(url, files=files, data=data)

    # Print out the response for debugging
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response Text:", response.text)

if __name__ == "__main__":
    post_audio()
