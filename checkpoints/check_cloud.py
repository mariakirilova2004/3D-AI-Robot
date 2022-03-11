import json
import os
import traceback

from aiy.cloudspeech import CloudSpeechClient

OLD_CREDENTIALS_FILE = os.path.expanduser('~/credentials.json')
NEW_CREDENTIALS_FILE = os.path.expanduser('~/cloud_speech.json')
if os.path.exists(OLD_CREDENTIALS_FILE):
    # Legacy fallback: old location of credentials.
    CREDENTIALS_PATH = OLD_CREDENTIALS_FILE
else:
    CREDENTIALS_PATH = NEW_CREDENTIALS_FILE

def check_credentials_valid():
    """Check the credentials are JSON service credentials."""
    try:
        obj = json.load(open(CREDENTIALS_PATH))
    except ValueError:
        return False

    return 'type' in obj and obj['type'] == 'service_account'

def check_speech_reco():
    path = os.path.join(os.path.dirname(__file__), 'test_hello.raw')
    with open(path, 'rb') as f:
        client = CloudSpeechClient()
        result = client.recognize_bytes(f.read())
        return result.strip() == 'hello'

def main():
    """Run all checks and print status."""
    if not os.path.exists(CREDENTIALS_PATH):
        print(
            "ERROR", CREDENTIALS_PATH)
        return

    if not check_credentials_valid():
        print(
            CREDENTIALS_PATH, """is not valid, please check that you have downloaded JSON
service credentials.""")
        return

    if not check_speech_reco():
        print('Failed to test the Cloud Speech API. Please see error above.')
        return

    print("Everything is set up to use the Google Cloud.")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        input('Press Enter to close...')
