import re


# From https://github.com/yhat/rodeo/issues/90#issuecomment-98790197
def slugify(text):
    return re.sub(r'[-\s]+', '_', (re.sub(r'[^\w\s-]', '', text).strip().lower()))
