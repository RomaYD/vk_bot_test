import requests
from config import TOKEN, GROUP

ACCESS_TOKEN = TOKEN
GROUP_ID = GROUP
API_VERSION = '5.199'
API_URL = 'https://api.vk.com/method/'

def send_message(user_id, message):
    requests.post(API_URL + 'messages.send', data={
        'user_id': user_id,
        'message': message,
        'access_token': ACCESS_TOKEN,
        'v': API_VERSION,
        'random_id': 0
    })

def send_photo(user_id, photo_url):
    photo_url = ','.join(photo_url)
    requests.post(API_URL + 'messages.send', data={
        'user_id': user_id,
        'attachment': photo_url,
        'access_token': ACCESS_TOKEN,
        'v': API_VERSION,
        'random_id': 0
    })

def main():
    longpoll_server = requests.get(API_URL + 'groups.getLongPollServer', params={
        'group_id': GROUP_ID,
        'access_token': ACCESS_TOKEN,
        'v': API_VERSION
    }).json()
    ts = longpoll_server['response']['ts']
    longpoll_url = f"{longpoll_server['response']['server']}?key={longpoll_server['response']['key']}&ts={ts}"

    while True:
        response = requests.get(longpoll_url).json()
        if 'updates' in response:
            for event in response['updates']:
                if event['type'] == 'message_allow':
                    user_id = event['object']['user_id']
                    message_history = requests.get(API_URL + 'messages.getHistory', params={
                        'group_id': GROUP_ID,
                        'access_token': ACCESS_TOKEN,
                        'v': API_VERSION,
                        'user_id': user_id,
                        'start_message_id': 0
                    }).json()
                    if message_history['response']['count'] == 0:
                        send_message(user_id, 'Привет! Отправь мне изображение, и я пришлю его обратно. :)')
                if event['type'] == 'message_new':
                    user_id = event['object']['message']['from_id']
                    attachments = event['object']['message'].get('attachments', [])
                    if attachments:
                        attachment_list = []
                        for attachment in attachments:
                            if attachment['type'] == 'photo':
                                at = f"photo{str(attachment['photo']['owner_id'])}_{str(attachment['photo']['id'])}"
                                if attachment['photo'].get('access_key'):
                                    at += '_' + str(attachment['photo']['access_key'])
                                attachment_list.append(at)
                        send_photo(user_id, attachment_list)
        ts = response['ts']
        longpoll_url = f"{longpoll_server['response']['server']}?key={longpoll_server['response']['key']}&ts={ts}"

if __name__ == '__main__':
    main()
