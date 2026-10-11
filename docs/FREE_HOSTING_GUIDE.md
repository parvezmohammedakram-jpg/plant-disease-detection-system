# 100% Free & Simple Hosting Guide — AI Plant Care System

If you want to host this application **without paying a single cent ($0.00)** and **without managing Linux servers or Docker terminal commands**, here are the **two simplest and best free options**.

---

## Comparison of Free Tier Options

| Platform | Difficulty | Free RAM | Setup Time | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Option 1: Render.com + MongoDB Atlas** | **Super Simple (1-Click UI)** | 512 MB | **5 minutes** | Easiest web app deployment directly from GitHub. |
| **Option 2: Hugging Face Spaces (Docker)** | **Very Simple** | **16 GB RAM!** | **3 minutes** | Best performance for Machine Learning (TensorFlow). |
| **Option 3: Google Cloud Run + MongoDB Atlas** | Moderate (CLI) | Up to 2 GB | 10 minutes | 2 Million requests/month free, auto-scaling. |

---

## 🚀 Option 1: Render.com + MongoDB Atlas (The Simplest & Most Popular)

Render connects directly to your GitHub repository and automatically builds and deploys the app whenever you push code.

### Step 1: Create a Free MongoDB Database on MongoDB Atlas (3 Minutes)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up for a free account.
2. Click **Create Deployment** → select **M0 (Free Forever)**.
3. Choose the region closest to you (e.g., **AWS Mumbai `ap-south-1`** or Singapore).
4. Under **Security / Database Access**:
   - Create a username (e.g. `plantcare_admin`) and a password (e.g. `GreenFarm2026!`).
5. Under **Security / Network Access**:
   - Click **Add IP Address** → choose **Allow Access from Anywhere (`0.0.0.0/0`)** (Render uses dynamic IP addresses).
6. Click **Connect** → **Drivers (Python)** → Copy your connection string:
   ```
   mongodb+srv://plantcare_admin:GreenFarm2026!@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   ```

---

### Step 2: Deploy to Render.com (2 Minutes)
1. Push your project code to your GitHub account (make sure it's in a repository).
2. Go to [Render.com](https://render.com) and sign in with GitHub.
3. In the Render Dashboard, click **New +** → **Web Service**.
4. Select your **`plant-disease-detection-system`** repository.
5. Fill in the settings (Render will auto-detect most of this from `render.yaml`):
   * **Name:** `plant-care-app` (or any name you choose)
   * **Runtime:** `Python 3`
   * **Build Command:**
     ```bash
     pip install -r requirements.txt && python -m babel.messages.frontend compile -d app/translations
     ```
   * **Start Command:**
     ```bash
     gunicorn -c gunicorn.conf.py run:app
     ```
   * **Instance Type:** Select **Free** ($0/month).
6. Under **Environment Variables**, click **Add Environment Variable** and add:
   * `APP_ENV` = `production`
   * `DEBUG` = `False`
   * `SECRET_KEY` = `any-random-long-secret-key-string-here`
   * `DATABASE_NAME` = `plant_disease_db`
   * `MONGODB_URI` = `mongodb+srv://plantcare_admin:GreenFarm2026!@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority` *(paste your Atlas string from Step 1)*
7. Click **Create Web Service**!
8. Render will build and deploy the application. Within 2–3 minutes, you will get a live URL:
   `https://plant-care-app.onrender.com`

> [!TIP]
> **Free Tier "Spin Down" Tip:** Render free services go to sleep after 15 minutes of inactivity (causing a ~40s delay when first opening). To keep it awake 24/7 for free, set up a free monitor at [UptimeRobot.com](https://uptimerobot.com) or [cron-job.org](https://cron-job.org) to ping your URL (`https://your-app.onrender.com/health`) every 10 minutes!

---

## ⚡ Option 2: Hugging Face Spaces (Best for ML — 16GB Free RAM!)

Hugging Face provides **16GB of RAM and 2 vCPU completely free** for AI/ML applications, making it ideal for running TensorFlow models without worrying about memory limits.

### Step-by-Step Setup:
1. Go to [Hugging Face](https://huggingface.co) and create a free account.
2. Click on your profile icon → **New Space**.
3. Fill in:
   * **Space name:** `plant-disease-detector`
   * **License:** `mit` (or choose yours)
   * **Space SDK:** Choose **Docker** → **Blank**.
   * **Space Hardware:** **CPU basic (2 vCPU · 16 GB RAM · Free)**.
4. In the Space Settings → **Variables and secrets**:
   * Add Secret `MONGODB_URI`: *(your MongoDB Atlas connection string)*
   * Add Variable `APP_ENV`: `production`
   * Add Variable `PORT`: `7860` (Hugging Face default)
5. Push your repository code to the Hugging Face Space git repository:
   ```bash
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/plant-disease-detector
   git push space main
   ```
6. Hugging Face builds the Docker container and serves your application at `https://your_username-plant-disease-detector.hf.space` with 16GB RAM for $0!

---

## ☁️ Option 3: Google Cloud Run (2 Million Free Requests/Month)

If you have a Google Cloud account, **Cloud Run** offers:
* **2,000,000 requests per month FREE**
* 360,000 vCPU-seconds FREE
* Auto-scales to 0 when nobody is using it (costs $0)
* Scales up instantly when a farmer uploads an image

### Deploy in 1 Command:
```bash
gcloud run deploy plant-care-app \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "APP_ENV=production,DATABASE_NAME=plant_disease_db,MONGODB_URI=your_atlas_uri"
```

---

## Summary Recommendation

* **For the fastest, easiest setup:** Use **Option 1 (Render.com + MongoDB Atlas)**. It requires zero command-line tools, links directly to your GitHub repo, and handles SSL certificates automatically.
* **For maximum AI/ML performance without memory limits:** Use **Option 2 (Hugging Face Spaces)** because it gives **16GB RAM for free**.
