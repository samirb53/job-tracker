# 💼 Job Application Tracker

A modern, user-friendly web application to track job applications with analytics, reminders, and insights.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/job-tracker.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the path to your app: `app.py`
   - Click "Deploy"

3. **Share the URL with your dad!**

## 🌟 Features

- **📝 Add Applications**: Comprehensive form with all job details
- **📊 Dashboard**: Smart alerts for deadlines, follow-ups, interviews
- **📈 Analytics**: Charts and insights about your job search
- **📅 Calendar**: Upcoming events and reminders
- **💾 Data Persistence**: Automatic saving and backup
- **📱 Mobile Friendly**: Works on all devices

## 📁 Project Structure

```
Jobapplication/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── job_applications.csv  # Data file (auto-created)
└── job_applications_backup.json  # Backup file
```

## 🔧 Customization

### Adding New Fields
Edit the `add_job_application()` function in `app.py` to add new form fields.

### Changing Colors
Modify the CSS in the `st.markdown()` section at the top of `app.py`.

### Data Storage
- Data is saved to `job_applications.csv`
- Automatic backup to `job_applications_backup.json`
- Data persists even if the app goes offline

## 🚀 Deployment Options

### 1. Streamlit Cloud (Recommended)
- **Free hosting**
- **Automatic updates** when you push to GitHub
- **Easy setup** - just connect your GitHub repo
- **Custom domain** support

### 2. Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-job-tracker
git push heroku main
```

### 3. Railway
- Connect your GitHub repo
- Automatic deployment
- Free tier available

### 4. Vercel
- Good for static sites
- Requires some configuration for Streamlit

## 📱 For Your Dad

Once deployed, your dad can:
- **Access from anywhere** using the URL
- **No installation needed** - just open in browser
- **Mobile friendly** - works on phones and tablets
- **Real-time updates** - see your latest applications instantly

## 🔒 Data Security

- **Local storage**: Data is saved on your device
- **No cloud storage**: Your job data stays private
- **Backup system**: Automatic JSON backup prevents data loss

## 🛠️ Troubleshooting

### Common Issues:
1. **Port already in use**: Change port in `.streamlit/config.toml`
2. **Import errors**: Make sure all requirements are installed
3. **Data not saving**: Check file permissions in the project directory

### Support:
- Check the Streamlit documentation
- Review the error messages in the terminal
- Ensure all dependencies are correctly installed

## 🎯 Next Steps

1. **Deploy to Streamlit Cloud** (easiest option)
2. **Share the URL** with your dad
3. **Add your first application** to test the system
4. **Customize** colors and fields as needed

Your dad will be impressed with this professional job tracking system! 🎉 