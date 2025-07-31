# SmartDoc AI 🤖📄

> **Backend Developer Internship Project** - A smart document summarization system that turns long documents into quick summaries using AI.

## 💡 What Does This Do?

Ever spent hours reading a 50-page report just to find the key points? **SmartDoc AI** solves that! 

- Upload any document (PDF, Word, or text file)
- Get an AI-generated summary in seconds
- Choose summary length: short, medium, or detailed
- Secure user accounts with admin controls

**Perfect for:** Students analyzing research papers, professionals reviewing reports, or anyone dealing with information overload.

---

## ✨ What Makes It Special

### � **Smart Features**
- **Multiple file formats** - PDF, DOCX, TXT all supported
- **AI-powered summaries** - Three different lengths to choose from  
- **Never fails** - Built-in fallback system ensures you always get a summary
- **Secure** - JWT authentication with user/admin roles

### 🤖 **Triple AI System** (This is the cool part!)
1. **OpenAI GPT** (primary) - High-quality cloud AI
2. **Ollama Mistral** (backup) - Free local AI that runs on your computer
3. **Simple extraction** (fallback) - Always works, even if AI fails

This means your app **never breaks** - if one AI fails, it tries the next one!

## 🛠️ Tech Stack

**Backend:** FastAPI (Python web framework)  
**Database:** SQLAlchemy with SQLite  
**Authentication:** JWT tokens with password hashing  
**AI:** OpenAI API + Ollama (local AI)  
**Email:** SendGrid for notifications  

## 🚀 How to Run This

### **What You Need:**
- Python 3.8 or newer
- That's it! Everything else gets installed automatically.

### **Quick Setup:**
```bash
# 1. Get the code
git clone https://github.com/YOUR_USERNAME/SmartDoc-AI.git
cd SmartDoc-AI

# 2. Set up Python environment  
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install everything
pip install -r requirements.txt

# 4. Create your .env file
# Create a file called .env in the project root with this content:
```

**Create `.env` file:**
```env
# Database (SQLite - no setup needed)
DATABASE_URL=sqlite:///./test.db

# Security (required - generate a secure key)
JWT_SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256

# AI Services (optional - but recommended)
OPENAI_API_KEY=your-openai-api-key-here

# Local AI (optional - free alternative)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Email notifications (optional)
EMAIL_API_KEY=your-sendgrid-api-key-here
EMAIL_FROM=your-email@domain.com
```

**Important notes:**
- **JWT_SECRET_KEY**: Make this long and random! You can use any password generator.
- **OPENAI_API_KEY**: Get this from https://platform.openai.com/api-keys (optional but gives better summaries)
- **EMAIL_API_KEY**: Get this from SendGrid if you want email notifications (optional)
- The app works without API keys - it will use basic summarization!

# 5. Start the server
uvicorn app.main:app --reload

# 6. Open your browser
# Go to: http://localhost:8000/docs
```

That's it! Your API is running with interactive documentation.

## 🎮 How to Use the API

### **Step 1: Create Account**
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "john", "email": "john@test.com", "password": "password123"}'
```

### **Step 2: Login & Get Token**
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=john&password=password123"
```
Copy the `access_token` from the response - you'll need it!

### **Step 3: Upload a Document**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -F "file=@your-document.pdf"
```

### **Step 4: Get AI Summary** ⭐
```bash
curl -X POST "http://localhost:8000/documents/DOCUMENT_ID/summarize" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"length": "medium"}'
```

**Summary options:** `"short"` (few sentences), `"medium"` (paragraph), `"long"` (detailed)

### **Bonus: Admin Features**
Admins can see all users and manage accounts. Just register with `"role": "admin"` in step 1.

## 🧪 Testing Your API

**Easiest way:** Open http://localhost:8000/docs in your browser. This gives you a nice interface to test everything!

**Manual testing:**
1. Start the server: `uvicorn app.main:app --reload`
2. Go to http://localhost:8000/docs
3. Try the endpoints in order: register → login → upload → summarize

**What should work:**
- ✅ User registration and login
- ✅ File upload (PDF, DOCX, TXT)  
- ✅ AI summarization with 3 different lengths
- ✅ Admin can see all users
- ✅ Secure endpoints require valid tokens

## 🎯 Internship Requirements ✅

This project covers **everything** needed for the backend internship:

| Required | What I Built | Status |
|----------|-------------|---------|
| **5+ REST endpoints** | **8 endpoints** | ✅ Exceeded |
| **Database integration** | SQLAlchemy with 3 tables | ✅ Complete |
| **LLM integration** | 3-tier AI system | ✅ Advanced |
| **Third-party API** | OpenAI + SendGrid | ✅ Multiple |
| **Error handling** | Comprehensive validation | ✅ Professional |
| **Documentation** | This README + auto-docs | ✅ Detailed |

**Bonus features I added:**
- JWT authentication & authorization
- Role-based access (admin/user)
- Multiple AI providers with failover
- Email notifications
- File processing for multiple formats

## � Complete Project Overview

**What this README covers:**
- ✅ **Project purpose** - What it does and why it's useful
- ✅ **Key features** - Triple AI system, file support, security
- ✅ **Tech stack** - FastAPI, SQLAlchemy, JWT, AI integration
- ✅ **Complete setup** - Step-by-step installation with .env file
- ✅ **API usage** - Real examples with cURL commands
- ✅ **Testing guide** - How to verify everything works  
- ✅ **Internship compliance** - Requirements mapping
- ✅ **Configuration** - Environment variables explained

**8 API Endpoints:**
1. `POST /auth/register` - Create new user account
2. `POST /auth/login` - User authentication  
3. `POST /documents/upload` - Upload PDF/DOCX/TXT files
4. `GET /documents/` - List your documents
5. `GET /documents/{id}` - Get specific document details
6. `POST /documents/{id}/summarize` - Generate AI summary ⭐
7. `GET /admin/users` - Admin: view all users
8. `DELETE /admin/users/{id}` - Admin: delete user

**File Support:** PDF, DOCX, TXT with automatic text extraction
**AI System:** OpenAI GPT → Ollama Mistral → Basic extraction (never fails!)
**Security:** JWT tokens, password hashing, role-based access (user/admin)

## 🔧 Quick Setup Notes
**Extra environment variables (all optional):**
- `OPENAI_API_KEY` - For premium AI summaries
- `EMAIL_API_KEY` - For sending notification emails  
- `JWT_SECRET_KEY` - For secure tokens (auto-generated if not set)

**Database:** Uses SQLite by default (no setup needed). For production, you can switch to PostgreSQL.

**AI Setup:** Works out of the box with basic summarization. Add OpenAI key for better results, or install Ollama for free local AI.

---

## 🎉 What I Learned Building This

This project taught me a lot about:
- **Building robust APIs** that handle errors gracefully
- **Integrating multiple AI services** with smart fallbacks
- **User authentication** and security best practices
- **Database design** with proper relationships
- **File processing** and text extraction
- **API documentation** and testing workflows

The coolest part? The AI never fails! If OpenAI is down, it uses local AI. If that fails, it still gives you a basic summary. Real-world reliability! 🚀

---

**Built for the Backend Developer Internship Program** 💻
