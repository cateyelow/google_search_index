# Google Search Console Indexing Tool Setup Guide

## 1. Google Cloud Console Setup

### 1.1 Project and API Activation
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select a project or create a new project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Google Search Console API" and enable it

### 1.2 Create OAuth 2.0 Client ID
1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth Client ID"
3. Application type: Select "Desktop Application"
4. Name: "Google Search Indexing Tool" (or any name you prefer)

### 1.3 Configure Authorized Redirect URIs (Important!)
In the OAuth Client ID settings, add the following URIs to "Authorized redirect URIs":

```
http://localhost:3000
http://localhost:8080
http://localhost:8081
http://localhost:8082
```

**⚠️ Important Notes:**
- URIs must be entered exactly as shown above (no trailing slash)
- Adding multiple ports makes the setup more robust
- Click Save after making changes

### 1.4 Download Client Secret File
1. Click the download button next to the created OAuth Client ID
2. Save the JSON file to your project folder
3. Ensure the filename is in the format `client_secret_XXXX.json`

## 2. Running the Program

### 2.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.2 Run the Program
```bash
python google_search_index_api.py
```

### 2.3 Authentication Process (Automated!)
1. The program will automatically start a local server
2. Your browser will open automatically
3. Log in with your Google account and authorize the application
4. After authorization, close the browser and return to the terminal

✅ **No need to manually enter authorization codes!**

## 3. Troubleshooting

### 3.1 "redirect_uri_mismatch" Error:
1. Double-check OAuth client settings in Google Cloud Console
2. Verify that the following redirect URIs are added:
   - http://localhost:3000
   - http://localhost:8080
   - http://localhost:8081
   - http://localhost:8082
3. Wait 5-10 minutes after saving changes (Google server propagation time)
4. Delete existing token file (`auto_token.pickle`) and retry

### 3.2 "Port already in use" Error:
- The program automatically tries different ports
- Multiple ports are configured, so this usually resolves automatically

### 3.3 "access_denied" Error:
1. Verify your Google account has Search Console permissions
2. Ensure the domain is registered in Search Console
3. Confirm your account is the owner or administrator of the domain

### 3.4 API Quota Exceeded Error:
1. Check API usage in Google Cloud Console
2. Request quota increase if needed
3. Be mindful of the daily limit (800 requests)

## 4. Program Configuration

You can modify the following values in the code as needed:

```python
# Inside main() function
sitemap_url = "https://textmachine.org/sitemap.xml"  # Sitemap URL
index_type = 1  # 1: Index registration, 0: Index deletion
daily_limit = 800  # Daily processing limit
```

## 5. Supported Features

- ✅ Automatic sitemap parsing
- ✅ Automatic local server startup
- ✅ Automatic browser opening
- ✅ Multiple port support
- ✅ Automatic retry mechanism
- ✅ Detailed logging
- ✅ Error handling and recovery
- ✅ API rate limit compliance

## 6. Log Files

All program activities are recorded in the `google_indexing.log` file.
Check this file to diagnose issues when errors occur. 