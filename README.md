# Jenkins Documentation for Sublime Text

A Sublime Text plugin that provides comprehensive documentation and autocompletion for Jenkins Pipeline syntax. This is a feature-complete port of the popular [JenkinsDocExtension](https://marketplace.visualstudio.com/items?itemName=Maarti.jenkins-doc) for VS Code.

Full credit to [Ryan Martinet](https://github.com/Maarti) for the original amazing project!

## ✨ Features

### 🔍 Rich Hover Documentation
Hover over Jenkins keywords to see beautifully formatted documentation:
- **Jenkins Pipeline steps** with detailed parameter information
- **Environment variables** with usage examples
- **Sections & Directives** with context information
- Parameter types (String, boolean, Enum) and optional/required status
- Direct links to official Jenkins documentation

### ⌨️ Intelligent Autocompletion

#### Parameter Autocompletion
- Type a function name and open parenthesis: `git(`
- Get intelligent suggestions for all available parameters
- Snippets automatically include proper formatting (`url: '$1'`, `branch: true`, etc.)
- See parameter types and whether they're optional right in the completion menu

#### Context-Aware Completions
- **Environment variables**: Type `env.` → Get all Jenkins environment variables
- **Post conditions**: Inside `post{}` blocks → Get condition completions (always, success, failure, etc.)
- **Smart snippets**: Sections/directives with inner instructions show available options
- **Multi-line detection**: Handles statements spanning multiple lines

### 🎯 Go to Definition
Navigate to Groovy function definitions across your project:
- Hover over `fileName.functionName` patterns
- Click "Go to definition" link in the popup
- Automatically searches `.groovy` files in your project
- Jumps directly to the function definition

### 📝 Smart Snippets
- Sections and directives include inner instruction hints
- Post blocks show available conditions
- Parameter completions include type-appropriate snippets

### 🎨 Beautiful UI
Custom HTML/CSS styling for documentation popups with:
- Syntax-highlighted code examples
- Color-coded parameter types
- Clear visual hierarchy
- Dark theme that matches Sublime Text

## 📦 Installation

### Package Control (Recommended)

1. Install [Package Control](https://packagecontrol.io/installation) if you haven't already
2. Open Command Palette (`Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on macOS)
3. Type: "Package Control: Install Package"
4. Search for "JenkinsDoc"
5. Press Enter to install

### Manual Installation

1. Download/clone this repository
2. Copy the `JenkinsDoc` folder to your Sublime Text Packages directory:
   - **Windows**: `%APPDATA%\Sublime Text\Packages\`
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
   - **Linux**: `~/.config/sublime-text/Packages/`
3. Restart Sublime Text

## 🚀 Usage

### Getting Started
The plugin automatically activates for:
- `.groovy` files
- `Jenkinsfile` (with or without extension)

### Autocompletion Examples

**Basic step completion:**
```groovy
// Type: git
// Result: git($1)  // Cursor positioned inside parentheses
```

**Parameter completion:**
```groovy
// Type: git(
// Get suggestions: url, branch, credentialsId, changelog, poll, etc.
// Select url → Result: url: '$1'
```

**Environment variables:**
```groovy
// Type: env.
// Get all variables: BUILD_NUMBER, WORKSPACE, JOB_NAME, etc.
```

**Post conditions:**
```groovy
post {
    // Type inside here to get: always, success, failure, etc.
}
```

### Hover Documentation
1. Hover mouse over any Jenkins keyword
2. View rich documentation in popup
3. Click documentation links to open official Jenkins docs

### Go to Definition
1. Write code like: `myUtils.deployToProduction()`
2. Hover over `myUtils.deployToProduction`
3. Click "Go to definition" in popup
4. Opens `myUtils.groovy` and jumps to `deployToProduction` function

### Commands
- **Command Palette**: `Jenkins: Show Documentation` - Display plugin information
- **Menu**: Tools → Jenkins Documentation → Show Documentation

## 🎯 Feature Comparison with VS Code Extension

| Feature | VS Code Extension | This Plugin | Status |
|---------|-------------------|-------------|--------|
| Hover Documentation | ✅ | ✅ | ✅ **Enhanced** with better styling |
| Basic Autocompletion | ✅ | ✅ | ✅ **100%** |
| Parameter Autocompletion | ✅ | ✅ | ✅ **100%** |
| Environment Variable Completion | ✅ | ✅ | ✅ **100%** |
| Go to Definition | ✅ | ✅ | ✅ **100%** |
| Smart Snippets with Enums | ✅ | ✅ | ✅ **100%** |
| Context-Aware Completions | ✅ | ✅ | ✅ **100%** |
| Multi-line Detection | ✅ | ✅ | ✅ **100%** |
| Post-block Detection | ✅ | ✅ | ✅ **100%** |
| Jenkinsfile Support | ✅ | ✅ | ✅ **100%** |
| Documentation Scraper | ✅ | ✅ | ✅ **Ported to Python** |

**Result: 100% feature parity achieved! 🎉**

## 🛠️ Updating Documentation Data

The plugin includes a Python scraper to fetch the latest Jenkins documentation:

```bash
cd scraper
pip install requests beautifulsoup4 lxml
python scraper.py
```

This generates an updated `jenkins_data.json` with the latest Jenkins Pipeline documentation.

See `scraper/README.md` for details.

## 📚 Supported Jenkins Features

### Pipeline Steps (500+)
All Jenkins Pipeline steps from popular plugins:
- Workflow Basic Steps, Git, Docker, Kubernetes
- SSH, HTTP Request, Email, Slack notifications
- And 100+ more plugins

### Environment Variables
`BUILD_NUMBER`, `BUILD_ID`, `JOB_NAME`, `WORKSPACE`, `JENKINS_URL`, and many more

### Sections
`agent`, `stages`, `stage`, `steps`, `post`

### Directives
`environment`, `options`, `parameters`, `triggers`, `tools`, `input`, `when`

### Post Conditions
`always`, `success`, `failure`, `unstable`, `changed`, `fixed`, `regression`, `aborted`, `unsuccessful`, `cleanup`

## 🐛 Troubleshooting

**Completions not showing?**
- Verify you're in a `.groovy` file or `Jenkinsfile`
- Try `Ctrl+Space` to manually trigger
- Check Sublime Text console: `Ctrl+` `

**Hover not working?**
- Ensure syntax is set to Groovy
- Verify `jenkins_data.json` exists in plugin directory

**Go to definition not working?**
- Open your project folder in Sublime Text (Project → Add Folder to Project)
- Ensure `.groovy` files exist in project

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork this repository
2. Make your changes
3. Test thoroughly in Sublime Text
4. Submit a pull request

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/JenkinsDoc-Sublime.git

# Symlink to Sublime Text Packages directory
ln -s $(pwd) "%APPDATA%\Sublime Text\Packages\JenkinsDoc"

# Restart Sublime Text
```

## 📄 License

GPL-3.0 License - Same as the original JenkinsDocExtension

## 🙏 Credits

- **Original Extension**: [JenkinsDocExtension](https://github.com/Maarti/JenkinsDocExtension) by [Ryan Martinet](https://github.com/Maarti)
- **Documentation Source**: [Jenkins.io](https://www.jenkins.io/doc/pipeline/steps/)
- **Sublime Text Port**: This project

## 🔗 Links

- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Jenkins Pipeline Steps Reference](https://www.jenkins.io/doc/pipeline/steps/)
- [Original VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Maarti.jenkins-doc)

## 📝 Version History

### 1.0.0 - Complete Feature Parity Release
- ✅ Rich hover documentation with enhanced HTML/CSS styling
- ✅ Smart autocompletion for all Jenkins Pipeline elements
- ✅ **Parameter autocompletion** inside function calls
- ✅ **Go to definition** for Groovy functions across files
- ✅ Context-aware completions with multi-line detection
- ✅ Smart snippets with enum value hints
- ✅ Post-condition block detection
- ✅ Jenkinsfile support (files without extensions)
- ✅ Python documentation scraper
- ✅ Comprehensive test coverage
- ✅ 100% feature parity with VS Code extension achieved!

---

**Happy Jenkins Pipeline coding! 🚀**

If you find this plugin helpful, please ⭐ star the repository!
