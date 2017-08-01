import backoff
import requests
import requests_cache
import time

from dragnet import ContentExtractionModel, content_extractor
from dragnet.diffbot_client import DiffbotClient
from dragnet.model_training import evaluate_models_tokens

content_extractor, evaluate_models_tokens
SKIMIT_API_URL = 'http://localhost:3001/api/extractions'

diffbot = DiffbotClient()
token = 'a2921a0004d2602f6e0e368ee876204d'
api = "article"


# @backoff.on_exception(backoff.expo, Exception, max_tries=3)
def call_diffbot(url):
    response = diffbot.request(url, token, api, fields=['title', 'text'], timeout=30000*1)
    time.sleep(2)
    if 'errorCode' in response:
        print('Failed to extract', url, response)
        return ''
    return response['objects'][0]['text']


class SkimitModel(ContentExtractionModel):
    def __init__(self):
        pass

    def analyze(self, s, **kwargs):
        # TODO make sure skimit extraction api is running on the specified address
        resp = requests.post(SKIMIT_API_URL, data=s, headers={'X-Forwarded-URL': 'hi'})
        ssai = resp.json()['SSAI']
        # 7.9.0 is the model version trained on the same data as dragnet
        assert ssai['model_versions']['content_model'] == '7.9.0'
        return ssai['text']


class DiffbotModel(SkimitModel):
    # TODO has to be updated each time ngrok is restarted
    # TODO make sure ngrok is running
    # TODO make sure the public server is running
    ngrok_url = 'http://66fe6474.ngrok.io'

    def __init__(self):
        # cache requests to diffbot because our key is limited
        # if we have to redo the evaluation we might exceed the quota
        requests_cache.install_cache('extractions_api_cache')

    def analyze(self, s, path=None, **kwargs):
        public_url = '%s/%s.html' % (self.ngrok_url, path)
        return call_diffbot(public_url)


if __name__ == '__main__':
    model, name = DiffbotModel(), 'diffbot'
    # model, name = SkimitModel(), 'skimit'
    # model, name = content_extractor, 'dragnet'

    evaluate_models_tokens('../content_data_2017-02-15-dragnet-format',
                           model,
                           content_or_comments='content',
                           figname_root='output_%s' % name,
                           limit_file='../content_data_2017-02-15-dragnet-format/test.txt',
                           limit_regex='.*' # TODO try 'smart.*'
                           )
