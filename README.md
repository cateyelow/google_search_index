# Google Search Console Indexing Tool

🚀 **Automated sitemap-based URL indexing for Google Search Console**

A Python tool that automatically extracts URLs from your sitemap and submits them to Google Search Console for indexing. This tool streamlines the process of getting your web pages indexed by Google, saving you time and ensuring comprehensive coverage of your site.

## ✨ Features

- 🗺️ **Automatic Sitemap Parsing** - Extracts URLs from XML sitemaps
- 🔐 **OAuth 2.0 Authentication** - Secure Google API integration
- 🌐 **Browser-based Auth** - No manual code copying required
- 🔄 **Multi-port Support** - Automatically tries different ports for local server
- 📊 **Batch Processing** - Submit multiple URLs efficiently
- ⚡ **Rate Limiting** - Respects Google API quotas
- 🔍 **Detailed Logging** - Comprehensive logging for debugging
- 🛡️ **Error Handling** - Robust error recovery and retry mechanisms
- 📈 **Progress Tracking** - Real-time processing status
- 🎯 **Daily Limits** - Configurable daily processing limits

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Google Cloud Console project with Search Console API enabled
- OAuth 2.0 credentials configured

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd google_search_index
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud Console** (See [Setup Guide](SETUP_GUIDE.md) for detailed instructions)

## 🚀 Quick Start

1. **Place your client secret file** in the project directory
2. **Run the tool**
   ```bash
   python google_search_index_api.py
   ```
3. **Authenticate** when prompted in your browser
4. **Monitor progress** in the terminal

## ⚙️ Configuration

### Default Settings

The tool comes with sensible defaults that you can customize:

```python
# In main() function
sitemap_url = "https://textmachine.org/sitemap.xml"  # Your sitemap URL
index_type = 1                                       # 1: Register, 0: Delete
daily_limit = 200                                    # URLs per day
```

### Customization Options

| Setting | Description | Default | Options |
|---------|-------------|---------|---------|
| `sitemap_url` | URL of your XML sitemap | `https://textmachine.org/sitemap.xml` | Any valid sitemap URL |
| `index_type` | Operation type | `1` (Register) | `1` = Register, `0` = Delete |
| `daily_limit` | Max URLs per run | `200` | Any positive integer |

## 📋 Usage Examples

### Basic Usage
```bash
python google_search_index_api.py
```

### Custom Sitemap
Edit the `sitemap_url` in `main()` function:
```python
sitemap_url = "https://yoursite.com/sitemap.xml"
```

### Delete URLs from Index
Change `index_type` to `0`:
```python
index_type = 0  # Delete URLs from index
```

## 📊 Output Example

```
2024-01-15 10:30:45,123 [INFO] === Google Search Console Indexing Tool ===
2024-01-15 10:30:45,124 [INFO] Sitemap URL: https://textmachine.org/sitemap.xml
2024-01-15 10:30:45,125 [INFO] Operation type: Index registration
2024-01-15 10:30:45,126 [INFO] Daily limit: 200
2024-01-15 10:30:45,127 [INFO] Starting Google API authentication...
2024-01-15 10:30:50,234 [INFO] Authentication completed successfully!
2024-01-15 10:30:51,345 [INFO] Extracted 150 URLs from sitemap.
2024-01-15 10:30:51,346 [INFO] Starting index registration with Google Search Console...
2024-01-15 10:30:52,456 [INFO] [1/150] Processing: https://textmachine.org/page1
2024-01-15 10:30:53,567 [INFO] Result: {'notifyTime': '2024-01-15T10:30:53.567Z'}
```

## 🔧 API Quotas & Limits

- **Daily Limit**: 200 URLs (configurable)
- **Rate Limiting**: 1 request per second (built-in)
- **Google API Quota**: 200 requests per day (free tier)

## 🐛 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `redirect_uri_mismatch` | OAuth URIs not configured | See [Setup Guide](SETUP_GUIDE.md#13-configure-authorized-redirect-uris-important) |
| `access_denied` | No Search Console permissions | Verify domain ownership in Search Console |
| `Port already in use` | Local server port conflict | Tool automatically tries different ports |
| `API quota exceeded` | Daily limit reached | Wait 24 hours or request quota increase |

### Debug Mode

Check the log file for detailed information:
```bash
tail -f google_indexing.log
```

## 📁 Project Structure

```
google_search_index/
├── google_search_index_api.py    # Main application
├── requirements.txt              # Python dependencies
├── SETUP_GUIDE.md               # Detailed setup instructions
├── README.md                    # This file
├── google_indexing.log          # Runtime logs
├── auto_token.pickle            # OAuth token (auto-generated)
└── client_secret_*.json         # Your Google OAuth credentials
```

## 🔒 Security Notes

- OAuth tokens are stored locally in `auto_token.pickle`
- Client secret files contain sensitive information - keep them secure
- Never commit credential files to version control

## 📈 Performance

- **Processing Speed**: ~1 URL per second (API rate limit)
- **Memory Usage**: Minimal (< 50MB)
- **Disk Usage**: < 1MB (excluding logs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Search Console API
- Google OAuth 2.0
- Python community for excellent libraries

## 📞 Support

- 📖 [Setup Guide](SETUP_GUIDE.md) - Detailed configuration instructions
- 🐛 [Issues](../../issues) - Report bugs or request features
- 💬 [Discussions](../../discussions) - Community support

---

**Made with ❤️ for better SEO and web indexing** 