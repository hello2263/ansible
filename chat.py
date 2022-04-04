from slacker import Slacker
import json
from flask import Flask, request, make_response
from datetime import datetime
import time
import pytz

token = "xoxb-3337896479552-3311261174037-8gtinA2F7fL8sXb9Parw3tsK" #이부분 api.slack.com에서 발급받은 부분 넣으세요

slack = Slacker(token)

app = Flask(__name__)


def get_answer(user_query):
    if user_query == '' or None:
        return "앗.. 아무것도 안쓰셨거나.. 혹은 아직 해석 불가 글자에요. 아직 그정도로 똑똑하진 않아요."
    elif user_query in answer_dict.keys():  # 결과 있으면 리턴
        return answer_dict[user_query]

def event_handler(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    string_slack_event = str(slack_event)
    if string_slack_event.find("{'type': 'user', 'user_id': ") != -1:  # 멘션으로 호출
        try:
            user_query = slack_event['event']['blocks'][0]['elements'][0]['elements'][1]['text']
            answer = get_answer(user_query)
            slack.chat.post_message(channel, answer)
            return make_response("ok", 200, )
        except IndexError:
            pass
    elif string_slack_event.find("'channel_type': 'im'") != -1:  # 다이렉트로 호출
        try:
            if slack_event['event']['client_msg_id']:
                user_query = slack_event['event']['text']
                answer = get_answer(user_query)
                slack.chat.post_message(channel, answer)
                return make_response("ok", 200, )
        except IndexError:
            pass
        except KeyError:
            pass

    message = "[%s] cannot find event handler" % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route('/', methods=['POST'])
def hello_there():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return event_handler(event_type, slack_event)
    return make_response("There are no slack request events", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
