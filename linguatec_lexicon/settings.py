from django.conf import settings


GRAMATICAL_CATEGORIES = getattr(settings, 'GRAMATICAL_CATEGORIES', (
    ('adj.', 'adjective'),
    ('adv.', 'adverb'),
    ('conj.', 'conjunction'),
    ('n.', 'noun'),
    ('v.', 'verb'),
))