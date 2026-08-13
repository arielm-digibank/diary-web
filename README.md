# Diary Web - Travel Diary (2001-2002)

A modernized static site for a personal Hebrew travel diary, originally built with Microsoft FrontPage in 2002.

## Quick Start

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies (for fix scripts)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run dev server with hot reload
npm start
```

The site will be available at **http://localhost:8080**

## Project Structure

```
diary-web/
├── src/                    # Source files (Eleventy input)
│   ├── _includes/          # Layouts and partials
│   ├── _data/              # Global data files
│   ├── entries/            # 228 diary pages
│   ├── images/             # 1,133 image assets (Git LFS)
│   └── index.html          # Main table of contents
├── scripts/                # Python scripts for batch fixes
├── _site/                  # Built output (gitignored)
├── eleventy.config.js      # Eleventy configuration
├── package.json            # Node.js dependencies
└── requirements.txt        # Python dependencies
```

## Development Phases

1. **Setup** - Project structure, git, preview (done)
2. **Fix** - Python scripts to repair broken links, strip legacy markup
3. **Redesign** - New responsive RTL template via Eleventy layouts
4. **Features** - Interactive index, AI-powered summaries, search

## Notes

- Content is in **Hebrew (RTL)**
- Images are tracked with **Git LFS**
- Original FrontPage site kept in `trip/` folder (gitignored, for reference only)
