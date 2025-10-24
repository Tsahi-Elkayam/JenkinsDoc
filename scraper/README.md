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
4. Generate `../jenkins_data.json`

## Note

The scraper may take several minutes to complete as it fetches documentation from hundreds of plugins. Please be patient and avoid interrupting the process.
