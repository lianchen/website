#!/usr/bin/env python3
"""Build the dependency-free academic homepage from content.json."""

import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
GROUPS = (
    ('working', 'working-papers', 'Working Papers'),
    ('revision', 'under-revision', 'Under Revision'),
    ('published', 'publications', 'Publications'),
)
PUBLICATION_TYPES = (
    ('all', 'All'),
    ('refereed', 'Refereed'),
    ('survey-conference', 'Survey & conference'),
)


def anchor(url, label, extra=''):
    return f'<a href="{escape(url, quote=True)}"{extra}>{escape(label)}</a>'


def asset_url(filename):
    version = sha256((ROOT / filename).read_bytes()).hexdigest()[:12]
    return f'{filename}?v={version}'


def linked_text(paragraph):
    text = paragraph['text']
    parts, cursor = [], 0
    for link in sorted(paragraph['links'], key=lambda item: item['start']):
        start, end = link['start'], link['end']
        assert start >= cursor and text[start:end] == link['text'], 'Invalid inline link offsets'
        parts.extend((escape(text[cursor:start]), anchor(link['url'], link['text'])))
        cursor = end
    parts.append(escape(text[cursor:]))
    return ''.join(parts)


def linked_paragraph(paragraph):
    return '<p>' + linked_text(paragraph) + '</p>'


def paper_html(paper):
    badge = f'<span class="badge">{escape(paper["badge"])}</span>' if paper.get('badge') else ''
    coauthors = f' <span class="coauthors">(with {escape(paper["coauthors"])})</span>' if paper['coauthors'] else ''
    note = f'({linked_text(paper["note"])})' if paper.get('note') else ''
    details = ' '.join(part for part in (escape(paper['status']), note) if part)
    status = f'<p class="status">{details}</p>' if details else ''
    links = ' '.join('[' + anchor(link['url'], link['label']) + ']' for link in paper['links'])
    links = f' <span class="paper-links" aria-label="Additional materials">{links}</span>' if links else ''
    publication_type = f' data-publication-type="{escape(paper["publication_type"])}"' if paper['group'] == 'published' else ''
    return f'''<li class="paper" id="{escape(paper['id'])}" data-topics="{escape(' '.join(paper['topics']))}"{publication_type}>
  <div class="paper-main"><h4 class="paper-title">{badge}{anchor(paper['url'], paper['title'])}</h4>{coauthors}{links}</div>
  {status}
</li>'''


def teaching_html(offerings):
    courses = {}
    for offering in offerings:
        courses.setdefault(offering['course'], []).append(offering)
    entries = []
    for title, course_offerings in courses.items():
        terms = sorted({item['term'] for item in course_offerings}, key=lambda term: int(term.rsplit(' ', 1)[1]))
        seasons = {term.rsplit(' ', 1)[0] for term in terms}
        if len(seasons) == 1:
            years = [term.rsplit(' ', 1)[1] for term in terms]
            dates = years[0] if len(years) == 1 else ', '.join(years[:-1]) + ' & ' + years[-1]
            dates = terms[0].rsplit(' ', 1)[0] + ' ' + dates
        else:
            dates = ' & '.join(terms)
        links = ' '.join(
            '[' + anchor(link['url'], f'{link["label"]} ({offering["term"].rsplit(" ", 1)[1]})') + ']'
            for offering in course_offerings for link in offering['links']
        )
        links = f' <span class="course-links">{links}</span>' if links else ''
        entries.append(f'''<li>
  <p class="course-terms">{escape(dates)}</p>
  <div class="course-main"><h3 class="course-title">{escape(title)}</h3>{links}</div>
</li>''')
    return '\n'.join(entries)


def render(data):
    profile = data['profile']
    bio = '\n'.join(linked_paragraph(item) for item in profile['bio_paragraphs'])
    jump = ''.join(f'<span class="jump-item">{anchor("#" + section_id, title)}</span>' for _, section_id, title in GROUPS)
    filters = '<button type="button" class="filter-button" data-filter="all" aria-pressed="true">All</button>'
    filters += ''.join(
        f'<button type="button" class="filter-button" data-filter="{escape(topic["id"])}" aria-pressed="false" title="{escape(topic["source_label"], quote=True)}">{escape(topic["label"])}</button>'
        for topic in data['topics']
    )
    sections = []
    for group, section_id, title in GROUPS:
        papers = '\n'.join(paper_html(paper) for paper in data['papers'] if paper['group'] == group)
        publication_filters = ''
        if group == 'published':
            type_buttons = ''.join(
                f'<button type="button" class="filter-button" data-publication-filter="{key}" aria-pressed="{str(key == "all").lower()}">{escape(label)}</button>'
                for key, label in PUBLICATION_TYPES
            )
            publication_filters = f'<div class="publication-filters filter-buttons" role="group" aria-label="Publication type" hidden>{type_buttons}</div>'
        sections.append(f'''<section class="paper-group" id="{section_id}" aria-labelledby="{section_id}-title">
  <h3 class="group-title" id="{section_id}-title">{title}</h3>
  {publication_filters}
  <ul class="papers">{papers}</ul>
</section>''')
    teaching = teaching_html(data['teaching'])
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chen Lian | UC Berkeley Economics</title>
  <meta name="description" content="Chen Lian is an assistant professor of economics at UC Berkeley. Research in macroeconomics, behavioral economics, and finance.">
  <link rel="canonical" href="https://lianchen.github.io/">
  <meta name="theme-color" content="#275d80">
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="{asset_url('styles.css')}">
  <script src="{asset_url('site.js')}" defer></script>
</head>
<body id="top">
  <div class="view-anchor" id="research" aria-hidden="true"></div>
  <div class="view-anchor" id="teaching" aria-hidden="true"></div>
  <a class="skip-link research-only" href="#main">Skip to main content</a>
  <a class="skip-link teaching-only" href="#teaching-main">Skip to main content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="wordmark" href="#top">Chen <span class="surname">Lian</span></a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="#research" data-view="research">Research</a><a href="#teaching" data-view="teaching">Teaching</a>{anchor(profile['cv_url'], 'CV')}
      </nav>
    </div>
  </header>
  <main class="wrap" id="main">
    <div id="teaching-main"></div>
    <section class="profile" id="about" aria-labelledby="profile-title">
      <img class="portrait" src="{escape(profile['photo_path'])}" width="236" height="295" alt="Chen Lian" fetchpriority="high">
      <div>
        <h1 id="profile-title">Chen <span class="surname">Lian</span></h1>
        <p class="affiliation">{escape(profile['role'])} · {escape(profile['institution'])}</p>
        <div class="bio">{bio}</div>
        <div class="profile-links" aria-label="Profile links">
          {anchor(profile['cv_url'], 'CV')}{anchor(profile['scholar_url'], 'Google Scholar')}
          <span>Please see my {anchor(profile['research_statement_url'], 'research statement')} ({escape(profile['research_statement_date'])}) for a summary.</span>
        </div>
        <p class="contact"><span>{anchor('mailto:' + profile['email'], profile['email'])}</span><span>{escape(profile['office'])}</span></p>
      </div>
    </section>
    <section class="research-only" id="research-papers" aria-labelledby="research-title">
      <div class="research-heading">
        <h2 class="section-heading" id="research-title">Research</h2>
        <nav class="jump-links" aria-label="Research sections"><strong>Jump to:</strong>{jump}</nav>
      </div>
      <div class="research-tools">
        <fieldset class="topic-filters" hidden>
          <legend class="sr-only">Filter by topic</legend>
          <div class="filter-buttons">{filters}</div>
          <p class="sr-only" id="filter-status" role="status" aria-live="polite" aria-atomic="true"></p>
        </fieldset>
      </div>
      {''.join(sections)}
    </section>
    <section class="teaching teaching-only" aria-labelledby="teaching-title">
      <h2 class="section-heading" id="teaching-title">Teaching</h2>
      <ul class="teaching-list">{teaching}</ul>
    </section>
  </main>
</body>
</html>
'''


def document_urls(data):
    urls = [paper['url'] for paper in data['papers']]
    urls += [link['url'] for paper in data['papers'] for link in paper['links']]
    urls += [link['url'] for paper in data['papers'] for link in paper.get('note', {}).get('links', [])]
    urls += [link['url'] for course in data['teaching'] for link in course['links']]
    urls += [data['profile'][key] for key in ('cv_url', 'research_statement_url')]
    return urls


def validate(data):
    ids = [paper['id'] for paper in data['papers']]
    assert len(ids) == len(set(ids)), 'Duplicate paper identifiers'
    known_topics = {topic['id'] for topic in data['topics']}
    known_groups = {group for group, _, _ in GROUPS}
    for paper in data['papers']:
        assert paper['group'] in known_groups, f'Unknown group: {paper["group"]}'
        assert set(paper['topics']) <= known_topics, f'Unknown topic in {paper["title"]}'
        if paper['group'] == 'published':
            assert paper.get('publication_type') in {'refereed', 'survey-conference'}, f'Missing or invalid publication type: {paper["title"]}'
    for url in document_urls(data):
        parsed = urlparse(url)
        if parsed.netloc == 'lianchen.github.io' and parsed.path.startswith('/website/'):
            assert (ROOT / parsed.path.removeprefix('/website/')).is_file(), f'Missing linked local document: {url}'
        elif not parsed.scheme and not parsed.netloc:
            path = Path(parsed.path)
            assert not path.is_absolute() and '..' not in path.parts, f'Expected a relative document path: {url}'
            assert (ROOT / path).is_file(), f'Missing linked local document: {url}'
    assert (ROOT / data['profile']['photo_path']).is_file(), 'Missing portrait'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Also export just the public homepage assets to this directory')
    args = parser.parse_args()
    data = json.loads((ROOT / 'content.json').read_text())
    validate(data)
    (ROOT / 'index.html').write_text('\n'.join(line.rstrip() for line in render(data).splitlines()) + '\n')
    if args.output:
        destination = args.output.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        local_documents = {urlparse(url).path for url in document_urls(data) if not urlparse(url).scheme and not urlparse(url).netloc}
        public_files = {'index.html', 'styles.css', 'site.js', '.nojekyll', data['profile']['photo_path']} | local_documents
        for filename in sorted(public_files):
            target = destination / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / filename, target)
    counts = Counter(paper['group'] for paper in data['papers'])
    print(f'Built index.html: {len(data["papers"])} papers {dict(counts)}, {len(data["topics"])} topics, {len(data["teaching"])} teaching entries. Local document links verified.')


if __name__ == '__main__':
    main()
