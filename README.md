# 🧪 Universal Expiry Date Monitoring Platform

A professional web-based platform for monitoring expiry dates in Excel files with automatic email alerts.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Features

- ✅ **Universal Excel Compatibility** - Works with ANY Excel structure
- ✅ **Intelligent Detection** - Automatically finds expiry dates and item names
- ✅ **Multi-Sheet Support** - Processes all sheets in one go
- ✅ **Smart Extraction** - Captures lot numbers, locations, and other details
- ✅ **Professional Email Alerts** - Beautiful HTML-formatted notifications
- ✅ **Color-Coded Urgency** - Critical (red), Urgent (orange), Warning (yellow)
- ✅ **Downloadable Reports** - Export to Excel or CSV
- ✅ **Mobile Friendly** - Works on any device
- ✅ **No Installation** - Web-based platform

---

## 🚀 Quick Start

### Online Demo
Access the live platform: [Your URL Here]

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Open browser at: `http://localhost:8501`

---

## 📋 How to Use

1. **Upload** your Excel file
2. **Configure** warning period (default: 90 days)
3. **Click** "Check Expiry Dates"
4. **View** results with color-coded urgency
5. **Send** email alerts or download reports

---

## 💻 System Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for deployment)

---

## 📊 Supported Excel Formats

- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)
- `.csv` (Comma-separated values)

**Works with ANY structure:**
- Simple tables
- Complex spreadsheets
- Multiple sheets
- Different column orders
- Merged cells
- Various date formats

---

## 🎯 Use Cases

- 🧪 Laboratory reagent management
- 🏥 Medical supply tracking
- 🍕 Food inventory monitoring
- 💊 Pharmaceutical compliance
- 📦 Product shelf-life management
- 📄 License renewal tracking
- 🔧 Equipment calibration reminders

---

## ⚙️ Configuration

### Email Settings
Configure SMTP settings in the sidebar:
- **Gmail:** `smtp.gmail.com:587` (requires App Password)
- **Outlook:** `smtp-mail.outlook.com:587`
- **Custom:** Any SMTP server

### Warning Period
Adjust how many days before expiry to receive alerts (30-180 days).

### Sheet Exclusion
Skip specific sheets like Archive, Template, or Old Data.

---

## 🎨 Screenshots

### Main Interface
![Upload Screen](screenshots/upload.png)

### Results Display
![Results](screenshots/results.png)

### Email Alert
![Email](screenshots/email.png)

---

## 🔧 Development

### Project Structure
```
├── streamlit_app.py      # Main application
├── requirements.txt      # Python dependencies
├── DEPLOYMENT_GUIDE.md   # Deployment instructions
└── README.md            # This file
```

### Dependencies
- `streamlit` - Web framework
- `pandas` - Data processing
- `openpyxl` - Excel file handling
- `python-dateutil` - Date parsing

---

## 🚀 Deployment

### Streamlit Cloud (Free)
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

### Local Network
Run on company server for internal use:
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Cloud Platforms
- Heroku
- AWS
- Google Cloud
- Azure

---

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - How to deploy online
- [User Guide](USER_GUIDE.md) - How to use the platform
- [API Documentation](API.md) - For developers

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sara Abdullah**
- Email: saraabdullah7797@gmail.com
- GitHub: [@sara-abdullah](https://github.com/sara-abdullah)

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Data processing by [Pandas](https://pandas.pydata.org)
- Excel handling by [OpenPyXL](https://openpyxl.readthedocs.io)

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/sara-abdullah/expiry-monitoring-platform?style=social)
![GitHub forks](https://img.shields.io/github/forks/sara-abdullah/expiry-monitoring-platform?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/sara-abdullah/expiry-monitoring-platform?style=social)

---

## 🐛 Bug Reports

Found a bug? [Open an issue](https://github.com/sara-abdullah/expiry-monitoring-platform/issues)

---

## 💡 Feature Requests

Have an idea? [Open an issue](https://github.com/sara-abdullah/expiry-monitoring-platform/issues) with the label `enhancement`

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

**Built with ❤️ by Sara Abdullah**
