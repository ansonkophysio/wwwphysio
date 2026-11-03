# Source for www.wwwphysio.com

The website files at the top of this repository are generated. Do not edit them by hand.

- `posts/` (Chinese) and `posts-en/` (English) hold one HTML file per article, with the same file name in both, each starting with a JSON header comment.
- `src/` holds the stylesheet and images.
- `build.py` builds the site: run `python3 build.py`, then copy `dist/` to the top of the repository.
