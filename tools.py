from urllib.parse import urlparse


def make_absolute_url(base_url, url):
    base_url = str(urlparse(base_url).scheme) + "://" + str(urlparse(base_url).netloc)
    if (str(url).startswith("http")):
        return url
    else:
        return str(base_url) + str(url)


def sub_spaces(word, last_word):
    dl = len(last_word) - len(word)
    return dl if dl > 0 else 0


def print_inline(word, last_word):
    spaces = sub_spaces(word, last_word)
    print(word, ' '*spaces, end="\r")