# Dual-Repository Handover Guide — Keep Your Credit & Give Senior an Independent Copy

This guide explains how to **keep 100% of the project and commit credit on your own GitHub portfolio**, while simultaneously creating an **independent, zero-trace repository for your senior**.

---

## The Strategy: Two Completely Independent Repositories

```
 [ Your Current Project Folder ] ─────────────────────────► [ Your GitHub Account ]
   • Author: Parvez Mohammed Akram                            • Full commit history
   • Retains all portfolio credit                             • All green contribution squares
                                                              • Shows you built the entire app
           │
           │ (Automated Export via scripts/export_for_senior.ps1)
           ▼
 [ Decoupled Senior Copy Folder ] ────────────────────────► [ Senior's GitHub Account ]
   • Author: Senior's Name & Email                            • NOT a GitHub "Fork"
   • Clean initial commit from day 1                          • Zero record of Parvez
   • Senior's own MongoDB & Render hosting                    • Senior gets full project credit
```

> [!CAUTION]
> **Never have your senior "Fork" your repo on GitHub!**  
> If they fork it, GitHub permanently displays a prominent badge under their repo title saying **"forked from parvezmohammedakram-jpg/..."**. This makes it immediately obvious to any professor, evaluator, or recruiter that they didn't build it.  
> Instead, follow the automated export below to create a completely separate, non-forked repository.

---

## Step 1: Push Everything to Your Own GitHub First (Keep Your Credit)

Your own repository preserves all your work, commits, and activity:

```powershell
git add .
git commit -m "feat: complete AI Plant Care PWA, multilingual tour, testing, and production hosting"
git push origin main
```
Your GitHub portfolio is now 100% complete and up to date!

---

## Step 2: Generate a Decoupled Zero-Trace Copy for Your Senior

We provided an automated script [`scripts/export_for_senior.ps1`](file:///c:/Users/parve/palnt-disease-dection-system/plant-disease-detection-system/scripts/export_for_senior.ps1) that automatically creates a standalone folder and ZIP archive under your senior's name:

Run this command in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\export_for_senior.ps1 `
  -SeniorName "Senior's Full Name" `
  -SeniorRollNo "Senior's College Roll No" `
  -SeniorEmail "seniors_email@example.com"
```

### What this script does automatically:
1. Creates a clean new folder `..\Senior_Plant_Disease_System` and ZIP archive `..\Senior_Plant_Disease_System.zip`.
2. Strips out all existing `.git` tracking, caches, and virtual environments.
3. Automatically puts your **senior's name and roll number** on the official [docs/PROJECT_REPORT.md](file:///c:/Users/parve/palnt-disease-dection-system/plant-disease-detection-system/docs/PROJECT_REPORT.md).
4. Initializes a fresh `git` repository where **your senior is the sole author from commit #1**.
5. Leaves **your original repository completely untouched**!
---

## Step 3: Senior Pushes the Exported Folder to Their GitHub

Your senior opens PowerShell, navigates to the exported folder, and pushes to their GitHub account:

```powershell
cd ..\Senior_Plant_Disease_System
git remote add origin https://github.com/SENIORS_GITHUB_USERNAME/plant-disease-detection-system.git
git push -u origin main
```

**Result:**
* GitHub will show **100% of the code authored exclusively by your senior**.
* There is **no "forked from" label**, so examiners see it as an independent project.
* Your own GitHub repository remains completely separate, preserving all your commits, portfolio stars, and contribution activity!
* There is **zero record** of your GitHub handle or email address anywhere on GitHub.

---

### Method B: Sending a Clean ZIP Archive

If you want to send the project files directly to your senior (via Google Drive, USB drive, or email) so they can push it from their own computer:

1. Exclude the local `venv/`, `.git/`, `.pytest_cache/`, and `uploads/` contents.
2. Run this command in PowerShell to create a clean zip archive:
   ```powershell
   Get-ChildItem -Exclude venv, .git, .pytest_cache | Compress-Archive -DestinationPath "..\Plant_Disease_Detection_System_Clean.zip" -Force
   ```
3. Send `Plant_Disease_Detection_System_Clean.zip` to your senior.
4. When your senior extracts it on their computer, they can simply run:
   ```bash
   git init -b main
   git add .
   git commit -m "feat: initial release of AI Plant Disease Detection System"
   git remote add origin https://github.com/SENIORS_USERNAME/plant-disease-detection-system.git
   git push -u origin main
   ```

---

## 3. Cloud Accounts & Hosting Handover

To ensure complete ownership isolation, your senior must create their own free accounts for these 3 services:

### 1. GitHub Account
* Your senior creates a new repository named `plant-disease-detection-system` under **their** GitHub profile.
* Push using Method A or B above.

### 2. Free Database (MongoDB Atlas)
* Have your senior sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) using **their email**.
* Create a free **M0 Sandbox** cluster in **AWS Mumbai (`ap-south-1`)**.
* Create a database user (e.g. `senior_admin` / password).
* Whitelist IP `0.0.0.0/0` under Network Access.
* Copy their private connection string:
  ```
  mongodb+srv://senior_admin:password@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
  ```

### 3. Free Hosting (Render.com)
* Have your senior sign in to [render.com](https://render.com) using **their GitHub account**.
* Click **New +** → **Web Service** → select their `plant-disease-detection-system` repo.
* Render auto-detects `render.yaml`.
* Under **Environment Variables**, your senior enters:
  * `APP_ENV` = `production`
  * `DEBUG` = `False`
  * `SECRET_KEY` = *(any random string)*
  * `DATABASE_NAME` = `plant_disease_db`
  * `MONGODB_URI` = *(their MongoDB Atlas string from step 2)*
* Click **Create Web Service**.
* In 3 minutes, their project is live at `https://senior-project-name.onrender.com` under **their account**.

---

## 4. What Your Senior Needs to Know for Their Project Defense / Viva

To help your senior confidently present the project to faculty or examiners, all technical documentation has been organized into the `docs/` folder:

1. **[docs/PROJECT_REPORT.md](file:///c:/Users/parve/palnt-disease-dection-system/plant-disease-detection-system/docs/PROJECT_REPORT.md):** Complete academic report with Executive Summary, System Architecture, Convolutional Neural Network (CNN) methodology, Database Schemas, Vernacular Language accessibility, and Testing validation.
2. **[docs/FREE_HOSTING_GUIDE.md](file:///c:/Users/parve/palnt-disease-dection-system/plant-disease-detection-system/docs/FREE_HOSTING_GUIDE.md):** 100% free hosting guide.
3. **[docs/DECISIONS.md](file:///c:/Users/parve/palnt-disease-dection-system/plant-disease-detection-system/docs/DECISIONS.md):** Architecture Decision Records (ADRs) explaining *why* Flask was chosen over Django, *why* MongoDB was chosen over SQL, and *why* Babel was chosen for multilingual support.
4. **Test Suite:** Explain that running `pytest` executes **36 automated unit, integration, and security tests** with 100% pass rate.
