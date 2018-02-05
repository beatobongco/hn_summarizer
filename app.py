import requests
from flask import Flask, render_template, request
from textteaser import TextTeaser
from bs4 import BeautifulSoup
from readability import Document

app = Flask(__name__)


def summarize_url(url, arc90=False):
  # arc90 helps us get the content of the article without the comments and shit
  # used in Safari's Reader view, Flipboard, and Treesaver.
  # https://stackoverflow.com/questions/4672060/web-scraping-how-to-identify-main-content-on-a-webpage

  CHAR_LIMIT = 100000 # blocks urls that have too much text that would bog us down
  # TODO: save results so that we avoid querying the same thing again
  # URL's can be PKs

  if not url:
    return

  r = requests.get(url)
  tt = TextTeaser()

  if arc90:
    doc = Document(r.text)
    title = doc.title()
    soup = BeautifulSoup(doc.summary(), "html.parser")
  else:
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.text

  text = ' '.join(map(lambda p: p.text, soup.find_all('p')))

  if len(text) < CHAR_LIMIT:
    summary = ' '.join(tt.summarize(title, text))
  else:
    summary = 'Text exceeds the ' + str(CHAR_LIMIT) + ' character limit.'

  return {'title': title, 'url': url, 'length': len(text), 'summary': summary,
          'minutes': len(text.split(' ')) // 200}


def get_daemonology_links():
  r = requests.get('http://www.daemonology.net/hn-daily/')
  soup = BeautifulSoup(r.text, "html.parser")
  links = [a['href'] for a in soup.find('ul').find_all('a')]
  print links
  return links


@app.route("/")
def hello():
  summaries = []
  links = get_daemonology_links()
  for link in links:
    summaries.append(summarize_url(link, arc90=True))

  return render_template('index.html', summaries=summaries)


@app.route('/u')
def wow():
  normal = summarize_url(request.args.get('q'))
  arc90 = summarize_url(request.args.get('q'), arc90=True)
  return render_template('index.html', summaries=[normal, arc90])
