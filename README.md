# JenkinsDoc - Jenkins Pipeline Documentation for Sublime Text

Jenkins Pipeline documentation and autocompletion plugin for Sublime Text.

**Author:** Tsahi Elkayam
**Repository:** [https://github.com/Tsahi-Elkayam/JenkinsDoc](https://github.com/Tsahi-Elkayam/JenkinsDoc)
**License:** GPL-3.0

Ported from the [JenkinsDocExtension](https://marketplace.visualstudio.com/items?itemName=Maarti.jenkins-doc) for VS Code by Ryan Martinet.

## Features

### Hover Documentation
Hover over Jenkins keywords to see documentation popups with:
- Step descriptions and parameters
- Environment variable info
- Links to official Jenkins docs
- Parameter types and whether they're optional

### Autocompletion
- Type `git` and get `git($1)` with cursor inside parentheses
- Type `git(` and get parameter suggestions (url, branch, credentialsId, etc.)
- Type `env.` and get all Jenkins environment variables
- Type inside `post{}` blocks to get condition completions (always, success, failure, etc.)
- Multi-line statement support

### Go to Definition
- Hover over custom function calls like `myUtils.deployToProduction()`
- Click the "Go to definition" link
- Jumps to the function in your `.groovy` files

### Status Bar
Shows "JenkinsDoc" in the status bar when editing Jenkins files.

## Installation

### Via Package Control (Recommended)

1. Install [Package Control](https://packagecontrol.io/installation)
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run "Package Control: Install Package"
4. Search for "JenkinsDoc"
5. Install

### Manual Installation

1. Clone or download this repository
2. Copy to your Sublime Text Packages folder:
   - Windows: `%APPDATA%\Sublime Text\Packages\`
   - macOS: `~/Library/Application Support/Sublime Text/Packages/`
   - Linux: `~/.config/sublime-text/Packages/`
3. Restart Sublime Text

## Configuration

Access via: Preferences → Package Settings → JenkinsDoc → Settings

```json
{
    "enabled": true,
    "show_status_bar": true,
    "show_hover_docs": true,
    "enable_autocompletion": true,
    "detect_jenkinsfile": true,
    "detect_groovy_files": true,
    "additional_file_patterns": []
}
```

## Usage

The plugin activates automatically for `.groovy` files and `Jenkinsfile`.

**Autocompletion examples:**

```groovy
// Type: git
// Get: git($1)

// Type: git(
// Get suggestions: url, branch, credentialsId, changelog, poll, etc.

// Type: env.
// Get: BUILD_NUMBER, WORKSPACE, JOB_NAME, etc.

post {
    // Type here to get: always, success, failure, etc.
}
```

## Testing

The `examples/` folder has test files you can use to verify everything works:

- `examples/test-Jenkinsfile` - Full test suite with 15+ feature tests
- `examples/utils.groovy` - Sample functions for testing go-to-definition

Open `examples/test-Jenkinsfile` in Sublime and follow the instructions.

## Updating Documentation Data

The plugin includes a scraper to fetch the latest Jenkins documentation:

```bash
cd scraper
pip install requests beautifulsoup4 lxml
python scraper.py
```

This updates `jenkins_data.json` with current Jenkins Pipeline docs. See `scraper/README.md` for configuration options.

## What's Included

**Pipeline Steps:** 500+ steps from popular plugins (Git, Docker, Kubernetes, SSH, HTTP, Email, Slack, etc.)

**Environment Variables:** BUILD_NUMBER, BUILD_ID, JOB_NAME, WORKSPACE, JENKINS_URL, and more

**Sections:** agent, stages, stage, steps, post

**Directives:** environment, options, parameters, triggers, tools, input, when

**Post Conditions:** always, success, failure, unstable, changed, fixed, regression, aborted, unsuccessful, cleanup

## Troubleshooting

**No completions showing?**
- Make sure you're in a `.groovy` file or `Jenkinsfile`
- Try `Ctrl+Space` to trigger manually
- Check Sublime console for errors (`Ctrl+\``)

**Hover not working?**
- Set syntax to Groovy if it's not detected automatically
- Check that `data/jenkins_data.json` exists

**Go to definition not working?**
- Open your project folder in Sublime (Project → Add Folder to Project)
- Make sure your `.groovy` files are in the project

## Feature Parity with VS Code Extension

This plugin has full feature parity with the original VS Code extension:

| Feature | Implemented |
|---------|-------------|
| Hover Documentation | Yes |
| Basic Autocompletion | Yes |
| Parameter Autocompletion | Yes |
| Environment Variable Completion | Yes |
| Go to Definition | Yes |
| Smart Snippets with Enums | Yes |
| Context-Aware Completions | Yes |
| Multi-line Detection | Yes |
| Post-block Detection | Yes |
| Jenkinsfile Support | Yes |
| Documentation Scraper | Yes (Python) |

## Contributing

Fork, make changes, test, and submit a PR. See `contributing.md` for details.

Development setup:
```bash
git clone https://github.com/Tsahi-Elkayam/JenkinsDoc.git
cd JenkinsDoc
pip install -r tests/requirements-dev.txt
```

## Credits

- Original VS Code extension: [JenkinsDocExtension](https://github.com/Maarti/JenkinsDocExtension) by Ryan Martinet
- Documentation source: [Jenkins.io](https://www.jenkins.io/doc/pipeline/steps/)

## Resources

Useful resources for Sublime Text plugin development:

- [OdatNurd YouTube Channel](https://www.youtube.com/@OdatNurd) - Sublime Text plugin tutorials and deep dives
- [Sublime Text Documentation](https://docs.sublimetext.io/) - Official plugin API docs
- [Sublime Text Guide](https://www.sublimetext.com/docs/) - User documentation
- [How to Create Your Own Sublime Text Plugin](https://medium.com/better-programming/how-to-create-your-own-sublime-text-plugin-2731e75f52d5) - Medium tutorial
- [Plugin Development Basics](https://www.reddit.com/r/SublimeText/comments/4q8m1a/sublime_text_plugin_development_basics/) - Reddit guide
- [How to Write a Sublime Plugin](https://vinted.engineering/2016/06/27/how-to-write-sublime-plugin/) - Vinted Engineering blog

## Support

If this plugin is useful to you, consider supporting development:

- [GitHub Sponsors](https://github.com/sponsors/Tsahi-Elkayam)
- [Buy Me a Coffee](https://buymeacoffee.com/tsahi.elkayam)
- [PayPal](https://paypal.me/etsahi)

## License

GPL-3.0 (same as the original extension)
