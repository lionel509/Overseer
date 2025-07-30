# Overseer Settings Guide

This guide explains all the configuration options available in Overseer, organized by category for easy reference.

## 📋 Table of Contents

1. [Basic LLM Configuration](#basic-llm-configuration)
2. [System Behavior Settings](#system-behavior-settings)
3. [File Management Settings](#file-management-settings)
4. [Security Settings](#security-settings)
5. [Search and Indexing Settings](#search-and-indexing-settings)
6. [UI and Interaction Settings](#ui-and-interaction-settings)
7. [Performance Settings](#performance-settings)
8. [Notification Settings](#notification-settings)
9. [Folder Configuration](#folder-configuration)
10. [Advanced Settings](#advanced-settings)

---

## 🔧 Basic LLM Configuration

### `llm_mode`
- **Type**: String
- **Options**: `'local'` | `'gemini'`
- **Default**: `'gemini'`
- **Description**: Choose between local LLM or online Gemini API

### `gemini_api_key`
- **Type**: String
- **Default**: `''`
- **Description**: Your Gemini API key for online LLM access

### `gemini_model_name`
- **Type**: String
- **Default**: `'gemini-2.5-flash-lite'`
- **Description**: Specific Gemini model to use

### `gemini_max_tokens`
- **Type**: Integer
- **Default**: `2048`
- **Description**: Maximum tokens for Gemini responses

### `gemini_temperature`
- **Type**: Float
- **Default**: `0.7`
- **Range**: `0.0` - `1.0`
- **Description**: Controls response creativity (higher = more creative)

### `local_model_name`
- **Type**: String
- **Default**: `'google/gemma-1.1-3b-it'`
- **Description**: Local model to use for inference

### `local_max_tokens`
- **Type**: Integer
- **Default**: `1024`
- **Description**: Maximum tokens for local model responses

### `local_temperature`
- **Type**: Float
- **Default**: `0.7`
- **Range**: `0.0` - `1.0`
- **Description**: Controls local model response creativity

---

## ⚙️ System Behavior Settings

### `debug`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable debug mode for detailed logging

### `log`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable general logging

### `verbose_output`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Show detailed output for operations

### `show_progress`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Display progress bars for long operations

### `auto_save`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Automatically save session data

---

## 📁 File Management Settings

### `file_indexing`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable file indexing for faster searches

### `auto_organize_enabled`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable automatic file organization

### `max_files_per_folder`
- **Type**: Integer
- **Default**: `100`
- **Description**: Maximum files per folder during auto-organize

### `confirm_moves`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Ask for confirmation before moving files

### `backup_before_move`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Create backup before moving files

### `scan_hidden_files`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Include hidden files in scans

### `exclude_patterns`
- **Type**: String
- **Default**: `'*.tmp,*.log,.DS_Store'`
- **Description**: Comma-separated file patterns to exclude

---

## 🔒 Security Settings

### `full_control`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable full control mode (bypass confirmations)

### `always_confirm_commands`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Always confirm before running system commands

### `sandbox_mode`
- **Type**: String
- **Options**: `'dry_run'` | `'simulation'` | `'isolated'` | `'validation'`
- **Default**: `'simulation'`
- **Description**: Default sandbox mode for command execution

### `command_timeout`
- **Type**: Integer
- **Default**: `30`
- **Description**: Command timeout in seconds

### `max_file_size`
- **Type**: Integer
- **Default**: `100`
- **Description**: Maximum file size to process (MB)

### `secure_config`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Use secure config manager with chmod 600

---

## 🔍 Search and Indexing Settings

### `search_depth`
- **Type**: Integer
- **Default**: `3`
- **Description**: How deep to search in directory structure

### `index_update_frequency`
- **Type**: Integer
- **Default**: `24`
- **Description**: How often to update file index (hours)

### `search_results_limit`
- **Type**: Integer
- **Default**: `50`
- **Description**: Maximum number of search results to return

### `fuzzy_search`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable fuzzy matching in searches

### `search_in_content`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Search within file contents (slower)

---

## 🎨 UI and Interaction Settings

### `color_output`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable colored terminal output

### `show_file_icons`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Show file type icons in listings

### `compact_mode`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Use compact display mode

### `auto_complete`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable command auto-completion

### `history_size`
- **Type**: Integer
- **Default**: `100`
- **Description**: Number of commands to remember in history

---

## ⚡ Performance Settings

### `max_threads`
- **Type**: Integer
- **Default**: `4`
- **Description**: Maximum concurrent threads for operations

### `cache_size`
- **Type**: Integer
- **Default**: `50`
- **Description**: Cache size in MB

### `memory_limit`
- **Type**: Integer
- **Default**: `512`
- **Description**: Memory limit in MB

### `batch_size`
- **Type**: Integer
- **Default**: `100`
- **Description**: Number of files to process in batches

---

## 🔔 Notification Settings

### `enable_notifications`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable system notifications

### `notification_sound`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Play sounds for notifications

### `email_notifications`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Send email notifications

---

## 📂 Folder Configuration

### `folders`
- **Type**: List of Strings
- **Default**: `['~/Downloads']`
- **Description**: Folders to watch and organize

### `auto_scan_folders`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Automatically scan watched folders

### `folder_scan_interval`
- **Type**: Integer
- **Default**: `60`
- **Description**: How often to scan folders (minutes)

---

## 🔧 Advanced Settings

### `log_level`
- **Type**: String
- **Options**: `'DEBUG'` | `'INFO'` | `'WARNING'` | `'ERROR'`
- **Default**: `'INFO'`
- **Description**: Logging level

### `log_file`
- **Type**: String
- **Default**: `'~/.overseer/overseer.log'`
- **Description**: Path to log file

### `temp_dir`
- **Type**: String
- **Default**: `'/tmp/overseer'`
- **Description**: Directory for temporary files

### `backup_dir`
- **Type**: String
- **Default**: `'~/.overseer/backups'`
- **Description**: Directory for file backups

---

## 🚀 Usage Examples

### Access Settings Menu
```bash
# Run settings editor
python -m overseer_cli --settings

# Or from chat mode
overseer> settings
```

### Example Configuration File
```json
{
  "debug": true,
  "log": true,
  "file_indexing": true,
  "full_control": false,
  "always_confirm_commands": true,
  "folders": ["/Users/user/Downloads"],
  "llm_mode": "gemini",
  "gemini_api_key": "your-api-key-here",
  "gemini_model_name": "gemini-2.5-flash-lite",
  "gemini_max_tokens": 2048,
  "gemini_temperature": 0.7,
  "auto_organize_enabled": true,
  "max_files_per_folder": 100,
  "confirm_moves": true,
  "sandbox_mode": "simulation",
  "command_timeout": 30,
  "search_depth": 3,
  "fuzzy_search": true,
  "color_output": true,
  "max_threads": 4,
  "cache_size": 50,
  "log_level": "INFO"
}
```

### Recommended Settings for Different Use Cases

#### **Development Environment**
```json
{
  "debug": true,
  "verbose_output": true,
  "search_in_content": true,
  "max_file_size": 500,
  "search_depth": 5
}
```

#### **Production Environment**
```json
{
  "debug": false,
  "verbose_output": false,
  "always_confirm_commands": true,
  "sandbox_mode": "validation",
  "secure_config": true
}
```

#### **High Performance**
```json
{
  "max_threads": 8,
  "cache_size": 100,
  "memory_limit": 1024,
  "batch_size": 200,
  "fuzzy_search": false
}
```

---

## 🔄 Updating Settings

### Method 1: Interactive Editor
```bash
python -m overseer_cli --settings
```

### Method 2: Direct File Edit
Edit `~/.overseer/config.json` directly (not recommended for sensitive settings)

### Method 3: Programmatic
```python
from overseer_cli import load_config, interactive_settings_editor

config = load_config()
config['debug'] = True
# Save changes...
```

---

## ⚠️ Important Notes

1. **Security**: Sensitive settings like API keys are automatically protected with `chmod 600`
2. **Validation**: Settings are validated when loaded
3. **Backup**: Always backup your config before major changes
4. **Restart**: Some settings require restart to take effect
5. **Defaults**: Missing settings will use sensible defaults

---

## 🆘 Troubleshooting

### Common Issues

**Q: Settings not saving?**
A: Check file permissions and ensure `~/.overseer/` directory exists

**Q: API key not working?**
A: Verify the key is correct and has proper permissions

**Q: Performance issues?**
A: Reduce `max_threads`, `cache_size`, or `search_depth`

**Q: Too many search results?**
A: Lower `search_results_limit` or increase `search_depth`

For more help, see the main documentation or run `python -m overseer_cli --help` 