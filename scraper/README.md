# Jenkins Documentation Scraper

This scraper fetches Jenkins Pipeline documentation from jenkins.io and generates the `jenkins_data.json` file used by the plugin.

## Requirements

```bash
pip install requests beautifulsoup4 lxml
```

## Setup

### Customize Configuration (Optional)

The scraper includes a `config.json` file with default settings. Edit it to customize the behavior:

```json
{
  "jenkins_base_url": "https://www.jenkins.io",
  "output_file": "../data/jenkins_data.json",
  "output_file_formatted": "../data/jenkins_data_formatted.json",
  "request_delay": 0.1,
  "save_formatted_version": false,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "environment_variables": [...]
}
```

## Configuration Options

### Core Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `jenkins_base_url` | string | `https://www.jenkins.io` | Base URL for Jenkins documentation |
| `output_file` | string | `../data/jenkins_data.json` | Output path for minified JSON |
| `output_file_formatted` | string | `../data/jenkins_data_formatted.json` | Output path for formatted JSON |
| `request_delay` | number | `0.1` | Delay (seconds) between HTTP requests |
| `save_formatted_version` | boolean | `false` | Save both minified and formatted versions |
| `user_agent` | string | Mozilla/5.0... | HTTP User-Agent header for requests |

### Environment Variables

The `environment_variables` array defines Jenkins environment variables to include in the output:

```json
"environment_variables": [
  {
    "name": "BUILD_NUMBER",
    "description": "The current build number"
  },
  {
    "name": "WORKSPACE",
    "description": "The absolute path of the workspace"
  }
]
```

You can add custom environment variables by appending to this array.

## Usage

```bash
python scraper.py
```

This will:
1. Load configuration from `config.json`
2. Fetch the list of Jenkins plugins from the configured Jenkins URL
3. Scrape each plugin's documentation page
4. Extract instructions (steps), parameters, sections, and directives
5. Generate `jenkins_data.json` (minified by default)

## Output Format

### Minified Output (Default)

By default, the scraper generates a **minified JSON file** with no whitespace to reduce file size and improve plugin loading performance:

- **File**: `jenkins_data.json`
- **Size**: ~1-2 MB (minified)
- **Usage**: Production use in the plugin

### Formatted Output (Optional)

Enable formatted output for debugging by setting `save_formatted_version: true` in `config.json`:

- **File**: `jenkins_data_formatted.json`
- **Size**: ~3-4 MB (formatted)
- **Usage**: Development and debugging

## Customization Examples

### Example 1: Change Output Location

```json
{
  "output_file": "/custom/path/jenkins_data.json"
}
```

### Example 2: Enable Formatted Output

```json
{
  "save_formatted_version": true
}
```

This generates both minified and formatted versions.

### Example 3: Adjust Request Delay

If you encounter rate limiting or want to be more respectful to the server:

```json
{
  "request_delay": 0.5
}
```

Increase from `0.1` to `0.5` seconds between requests.

### Example 4: Add Custom Environment Variables

```json
{
  "environment_variables": [
    {
      "name": "BUILD_NUMBER",
      "description": "The current build number"
    },
    {
      "name": "MY_CUSTOM_VAR",
      "description": "My custom Jenkins environment variable"
    }
  ]
}
```

### Example 5: Use Alternative Jenkins Instance

To scrape from a custom Jenkins instance (e.g., enterprise installation):

```json
{
  "jenkins_base_url": "https://jenkins.mycompany.com"
}
```

Note: The documentation structure must match the standard Jenkins.io format.

## Output Data Structure

The generated `jenkins_data.json` contains:

```json
{
  "date": "2024-01-15T10:30:00",
  "plugins": [...],
  "instructions": [...],
  "sections": [...],
  "directives": [...],
  "environmentVariables": [...]
}
```

- **plugins**: List of Jenkins plugins with URLs
- **instructions**: Pipeline steps with parameters and documentation
- **sections**: Pipeline sections (agent, stages, steps, etc.)
- **directives**: Pipeline directives (environment, options, etc.)
- **environmentVariables**: Jenkins environment variables

## Troubleshooting

### Error: Configuration file not found

**Problem**: `config.json` is missing from the scraper directory

**Solution**: Ensure you're running from the correct directory or check if the file was accidentally deleted. The repository includes a default `config.json` file.

### Error: Invalid JSON in configuration file

**Problem**: Syntax error in `config.json`

**Solution**: Validate your JSON using a JSON validator or check for:
- Missing commas
- Trailing commas
- Unquoted strings
- Missing brackets/braces

### Error: Connection timeout or rate limiting

**Problem**: Too many requests to Jenkins.io

**Solution**: Increase `request_delay` in `config.json`:
```json
{
  "request_delay": 0.5
}
```

## Performance Notes

- The scraper typically processes 100+ plugins
- Expected runtime: 2-10 minutes (depends on network speed and request delay)
- Output file size: 1-2 MB (minified), 3-4 MB (formatted)
- Please be respectful to Jenkins.io servers by not lowering `request_delay` below 0.1 seconds

## Advanced Usage

### Running with Custom Config File

```bash
# Not yet implemented, but config.json is the only supported file currently
python scraper.py
```

### Updating Only Environment Variables

If you only need to update environment variables without re-scraping:

1. Edit `config.json` and modify `environment_variables`
2. Run the scraper - it will use the updated variables

## Contributing

If you improve the scraper:

1. Update `config.json` with any new options and document them
2. Document new options in this README
3. Test with default configuration
4. Submit a pull request

## Notes

- The scraper may take several minutes to complete as it fetches documentation from hundreds of plugins
- Progress is shown in the console with plugin count and instruction count
- If interrupted, simply re-run the scraper - it starts fresh each time
- The output file is atomically written, so partial updates won't corrupt existing data
