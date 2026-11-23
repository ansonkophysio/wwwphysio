# Source for www.wwwphysio.com

The website files at the top of this repository are generated. Do not edit them by hand.

- `posts/` (Chinese) and `posts-en/` (English) hold one HTML file per article, with the same file name in both, each starting with a JSON header comment.
- `src/` holds the stylesheet and images.
- `build.py` builds the site: run `python3 build.py`, then copy `dist/` to the top of the repository.
- Share images: for each article with an SVG cover, `build.py` makes `src/img/share/<slug>.jpg` (1200×675) for link previews and the Article image. It needs `rsvg-convert` and Pillow; without them the build uses Anson's photo instead.
- Search engine verification: paste the Google Search Console or Bing Webmaster Tools "HTML tag" code into `GOOGLE_VERIFY` or `BING_VERIFY` in `build.py` and rebuild. The tag goes on the home page only.
- Structured data uses one Person (`/#anson`), one practice (`/#practice`) and one website (`/#website`). Keep team roles and non-registration certificates out of it (CoP 9.1–9.2).
