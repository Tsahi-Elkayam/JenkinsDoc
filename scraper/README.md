# Jenkins Documentation Scraper

This scraper fetches Jenkins Pipeline documentation from jenkins.io and generates the `jenkins_data.json` file used by the plugin.

## Requirements

```bash
pip install requests beautifulsoup4 lxml
```

## Usage

```bash
python scraper.py
```

This will:
1. Fetch the list of Jenkins plugins from https://www.jenkins.io/doc/pipeline/steps/
2. Scrape each plugin's documentation page
3. Extract instructions (steps), parameters, sections, and directives
4. Generate `../jenkins_data.json` (minified by default)

## Output Format

By default, the scraper generates a **minified JSON file** (no whitespace) to reduce file size and improve plugin loading performance.

If you need a formatted version for debugging:
1. Edit `scraper.py`
2. Set `SAVE_FORMATTED_VERSION = True`
3. Run the scraper - it will generate both:
   - `jenkins_data.json` (minified, ~25 MB)
   - `jenkins_data_formatted.json` (formatted, ~32 MB)

## Note

The scraper may take several minutes to complete as it fetches documentation from hundreds of plugins. Please be patient and avoid interrupting the process.
