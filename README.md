# Jenkins Documentation for Sublime Text

A Sublime Text plugin that provides documentation and autocompletion for Jenkins Pipeline syntax.

this is my attempt to fork https://marketplace.visualstudio.com/items?itemName=Maarti.jenkins-doc

full credit to ryan martinet for an amazing project
still under development

## Features

- Documentation on hover for Jenkins keywords
- Autocompletion for Jenkins commands and parameters
- Support for environment variables
- Documentation for sections and directives
- Post-condition completions

## Installation

### Package Control (Recommended)

1. Install [Package Control](https://packagecontrol.io/installation) if you haven't already
2. Open the Command Palette (Ctrl/Cmd + Shift + P)
3. Select "Package Control: Install Package"
4. Search for "Jenkins Documentation" and select it

### Manual Installation

1. Go to your Sublime Text packages directory:
   - Windows: `%APPDATA%\Sublime Text\Packages`
   - macOS: `~/Library/Application Support/Sublime Text/Packages`
   - Linux: `~/.config/sublime-text/Packages`
2. Clone this repository or copy all files into a new directory named `JenkinsDoc`

## Usage

- Hover over any Jenkins keyword to see its documentation
- Start typing to see autocompletions for Jenkins commands
- Type `env.` to see environment variable completions
- Inside a `post{}` block, get automatic post-condition completions

## Supported File Types

- Groovy files (\*.groovy)
- Jenkinsfile

## License

GPL-3.0
