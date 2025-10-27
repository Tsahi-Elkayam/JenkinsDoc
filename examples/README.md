# Examples

Just some example files to try out the plugin.

## Files

**Jenkinsfile** - Example pipeline showing off the main features. Comments explain what to try.

**utils.groovy** - Example Groovy functions for testing the go-to-definition feature.

## How to use

1. Open `Jenkinsfile` in Sublime Text
2. Look at the bottom-right - should say "JenkinsDoc"
3. Hover your mouse over keywords like `echo`, `sh`, `pipeline`
4. Try typing partial commands like `ec` and press Tab or Ctrl+Space
5. Type `env.` and watch the autocomplete show environment variables

That's basically it. The comments in the files explain the rest.

## Quick feature tour

**Hover docs** - Hover over any Jenkins keyword. You'll get a popup with docs, parameters, and a link to the official Jenkins docs.

**Autocomplete** - Start typing a command name. Press Tab or Ctrl+Space. Magic.

**Environment variables** - Type `env.` and you'll get all the Jenkins env vars (BUILD_NUMBER, JOB_NAME, etc).

**Parameter hints** - Type a command name followed by `(` like `git(` and you'll get parameter suggestions with types.

**Post conditions** - Inside a `post {}` block, type condition names like `success` or `failure`.

**Commands** - Press Ctrl+Shift+P (Cmd+Shift+P on Mac) and type "Jenkins" to see plugin commands.

## Troubleshooting

**Plugin not active?** (no "JenkinsDoc" in status bar)
- Make sure syntax is set to Groovy (bottom-right corner)
- Or rename your file to `Jenkinsfile` with no extension
- Or use `.groovy` extension

**No completions showing up?**
- Press Ctrl+Space to trigger manually
- Check View → Show Console for errors
- Try running "Jenkins: Diagnostics" from the command palette

**Hover not working?**
- Make sure `show_hover_docs` is `true` in settings
- Wait a moment - hover for about half a second
- Try different keywords (echo, pipeline, agent)

**Still broken?**
- Run "Jenkins: Reload Plugin" from command palette
- Check the main README for more troubleshooting
- File an issue on GitHub if all else fails

## Settings you might want to tweak

Open: Preferences → Package Settings → JenkinsDoc → Settings

```json
{
  "enabled": true,
  "show_hover_docs": true,
  "show_status_bar": true,
  "debug_mode": false,  // Set to true to see what's happening in console

  "detect_groovy_files": true,
  "detect_jenkinsfile": true,
  "additional_file_patterns": []  // Add custom patterns like ["*.jenkins"]
}
```

## Tips

- The Jenkinsfile has comments showing what features to try
- Set debug_mode to true if something's not working (then check console)
- The utils.groovy file shows how go-to-definition works with custom functions
- Copy these files and modify them for your own projects

---

If you find issues, report them on GitHub. If it works great, maybe give it a star!
