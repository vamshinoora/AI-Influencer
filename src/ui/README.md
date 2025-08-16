# 🎭 AI Influencer Web UI

A simple and intuitive web interface for managing AI personas and generating images.

## 🚀 Quick Start

### 1. Start the Application
```bash
# From project root
cd /Users/vnoora/Documents/GitHub/AI-Influencer
source .venv/bin/activate
python -m streamlit run src/ui/streamlit_app.py --server.port 8501
```

### 2. Access the Web Interface
Open your browser and go to: **http://localhost:8501**

## ✨ Features

### 👤 **User Management**
- **Register New Account**: Create user profile with business details
- **Login**: Access existing account with email
- **User Dashboard**: Overview of your personas and activity

### 🎭 **Persona Management**
- **Create AI Personas**: Define detailed character specifications
- **Visual Customization**: Set style, platform, and appearance preferences
- **Personality Traits**: Configure brand voice and content themes
- **Multiple Personas**: Manage different characters for different platforms

### 🎨 **Image Generation**
- **Select Persona**: Choose from your created AI characters
- **Custom Prompts**: Add specific details to generation
- **Platform Optimization**: Optimize for Instagram, LinkedIn, TikTok, etc.
- **Quality Settings**: Control generation parameters
- **Real-time Generation**: Live progress tracking

### 📜 **Generation History**
- **View All Generations**: Complete history of created images
- **Image Gallery**: See all your generated content
- **Generation Details**: Prompts, settings, and metadata
- **Platform Tracking**: See which platforms you generate for most

### 📊 **Analytics Dashboard**
- **Usage Statistics**: Total generations and personas
- **Platform Distribution**: Which platforms you use most
- **Recent Activity**: Latest generation attempts
- **Performance Metrics**: Success rates and satisfaction

## 🔧 System Requirements

### ✅ **Connected Services**
- **MongoDB Atlas**: ✅ Connected (`AiInfluensor` database)
- **ComfyUI**: ⚠️ Optional (falls back to mock mode)

### 📦 **Dependencies**
- Python 3.11+
- Streamlit 1.48+
- PyMongo 4.6+
- Pillow (PIL)

## 🎯 User Workflow

### 1. **First Time Setup**
1. Open http://localhost:8501
2. Create new account with business details
3. Fill in target audience and preferred platforms

### 2. **Create AI Personas**
1. Go to "🎭 Manage Personas"
2. Click "➕ Create New Persona"
3. Define character details:
   - Name and description
   - Style and platform
   - Visual preferences
   - Personality traits

### 3. **Generate Images**
1. Go to "🎨 Generate Images"
2. Select a persona
3. Add custom prompts (optional)
4. Configure settings
5. Click "🚀 Generate Image"

### 4. **View Results**
1. Go to "📜 Generation History"
2. See all your generated images
3. View generation details
4. Check analytics in "📊 Analytics"

## 🔗 Integration

### **MongoDB Atlas**
- All user data stored permanently
- Personas and generations tracked
- Images stored in GridFS
- Real-time analytics

### **ComfyUI (Optional)**
- Real image generation when available
- Falls back to mock mode for testing
- Progress tracking and error handling

## 🎨 UI Features

### **Responsive Design**
- Clean, modern interface
- Mobile-friendly layout
- Intuitive navigation

### **Real-time Updates**
- Live generation progress
- Automatic data refresh
- Instant feedback

### **Error Handling**
- Graceful degradation
- Clear error messages
- Fallback modes

## 🔧 Troubleshooting

### **MongoDB Not Connected**
- Check connection string in `mongodb_manager.py`
- Verify MongoDB Atlas cluster is running
- Check network connectivity

### **ComfyUI Not Available**
- App will run in mock mode
- Start ComfyUI server on localhost:8188
- Check ComfyUI installation

### **Port Already in Use**
```bash
# Use different port
python -m streamlit run src/ui/streamlit_app.py --server.port 8502
```

## 📱 Screenshots

The web interface includes:
- 🏠 **Dashboard**: User overview and quick actions
- 👤 **Profile**: User registration and management
- 🎭 **Personas**: Character creation and customization
- 🎨 **Generation**: Image creation with live progress
- 📜 **History**: Complete generation gallery
- 📊 **Analytics**: Usage statistics and insights

## 🚀 Production Deployment

For production deployment:
1. Configure proper MongoDB connection
2. Set up ComfyUI server
3. Use production WSGI server
4. Configure SSL/HTTPS
5. Set up proper authentication

---

**🎉 Your AI Influencer platform is ready to use!**
**Access at: http://localhost:8501**
