import requests

from dragnet import ContentExtractionModel, content_extractor
from dragnet.model_training import evaluate_models_tokens

content_extractor
SKIMIT_API_URL = 'http://localhost:3001/api/extractions'


class SkimitModel(ContentExtractionModel):
    def __init__(self):
        pass

    def analyze(self, s, blocks=False, encoding=None, parse_callback=None):
        resp = requests.post(SKIMIT_API_URL, data=s, headers={'X-Forwarded-URL': 'hi'})
        ssai = resp.json()['SSAI']
        # this is the model version trained on the same data as dragnet
        assert ssai['model_versions']['content_model'] == '7.9.0'
        return ssai['text']


if __name__ == '__main__':
    model, name = SkimitModel(), 'skimit'
    # model, name = content_extractor, 'dragnet'

    evaluate_models_tokens('../content_data_2017-02-15-dragnet-format',
                           model,
                           limit_file='../content_data_2017-02-15-dragnet-format/test.txt',
                           content_or_comments='content',
                           figname_root='output_%s' % name)
