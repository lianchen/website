# Chen Lian's academic website

A responsive, static homepage for `https://lianchen.github.io/`, with a compact profile and Hazell-style research navigation. No JavaScript framework or package installation is needed.

## Update the website

Edit `content.json` for papers, publication status, topic membership, teaching, and biography. Papers appear in the order they are listed within each group. A paper may have multiple topic IDs. Biography hyperlinks and optional paper-note hyperlinks use character offsets; update these if editing the corresponding text.

Published papers also need `publication_type`: `refereed` for journal articles or `survey-conference` for handbook chapters and conference contributions. The publication-type buttons appear only when the topic filter is All. Selecting any specific topic hides those buttons and resets publication type to All, so all publications matching that topic are shown.

Teaching records use `term`, `course`, and `links`. Records with the same course name appear together, with a combined semester line and year-labelled syllabus links. Keep a separate record for each semester taught.

Run `python3 build.py` to regenerate `index.html` and verify that linked documents exist. Both the content data and generated page should be included when committing an update. The page contains all content without JavaScript; the small script adds topic filtering.

Preview with `python3 -m http.server 8000 --bind 127.0.0.1`, then open `http://127.0.0.1:8000/`.

## Publishing

This repository, `lianchen/website`, already hosts PDFs at `https://lianchen.github.io/website/`. Keep those paths stable.

The root homepage is published from [lianchen/lianchen.github.io](https://github.com/lianchen/lianchen.github.io). This `website` repository contains its editable source and the existing paper archive.

After editing and rebuilding here, commit and push the source changes. In a checkout of `lianchen.github.io`, first pull the latest `main`, then export the public assets with `python3 build.py --output /path/to/homepage-checkout` from this repository. Commit and push the updated export in the homepage checkout. GitHub Pages publishes the homepage repository's `main` branch and root directory.

The export includes `index.html`, `styles.css`, `site.js`, `.nojekyll`, the profile photo, and any documents linked with relative URLs, including the 2026 bootcamp syllabus. Existing absolute PDF URLs stay on the original document site.

## Responsive behavior

The profile becomes a single column on phones. The navigation, research section links, and topic filters wrap. Selected filters have a filled state and a ring; keyboard focus is visible. Topic filters apply to all three publication groups. Empty groups and their section links are hidden. A screen-reader announcement reports the active topic without a visible summary line. Printing includes the full paper list regardless of the selected filter.
