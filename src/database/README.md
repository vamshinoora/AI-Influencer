# AI Influencer MongoDB Integration

## 🎯 Overview

Complete MongoDB integration for the AI Influencer system, providing persistent data storage for users, personas, generated content, and analytics.

## ✅ Implementation Status

### Core Features Implemented
- ✅ **User Management**: Complete CRUD operations for user profiles
- ✅ **Persona Management**: Store and manage AI character personas
- ✅ **Generation Logging**: Track all image generation attempts and results
- ✅ **Image Storage**: GridFS integration for storing generated images
- ✅ **Analytics System**: User statistics and generation metrics
- ✅ **Session Management**: User session tracking and management
- ✅ **Error Handling**: Comprehensive error handling and validation

### Database Schema
```
ai_influencer/
├── users/           # User profiles and preferences
├── personas/        # AI character definitions
├── generations/     # Generation history and logs
├── sessions/        # User session data
└── fs.files/        # GridFS image storage
    fs.chunks/
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pymongo
```

### 2. Set Up MongoDB Connection
```bash
# Option 1: Environment variable
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"

# Option 2: MongoDB Atlas
export MONGODB_CONNECTION_STRING="mongodb+srv://username:password@cluster.mongodb.net/"
```

### 3. Basic Usage
```python
from database.mongodb_manager import AIInfluencerDB

# Initialize database
db = AIInfluencerDB()

# Create user
user_id = db.create_user({
    "username": "my_business",
    "email": "user@business.com",
    "business_type": "E-commerce"
})

# Create persona
persona_id = db.create_persona({
    "user_id": user_id,
    "character_name": "Brand Ambassador",
    "description": "Professional spokesperson",
    "style": "professional"
})

# Log generation
generation_id = db.log_generation({
    "user_id": user_id,
    "persona_id": persona_id,
    "generation_type": "image",
    "prompt_used": "Professional headshot",
    "platform_optimized": "linkedin"
})
```

## 🔧 MongoDB Setup Options

### Option 1: Local MongoDB
```bash
# Install MongoDB (macOS)
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Test connection
mongosh
```

### Option 2: MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create cluster and database user
3. Get connection string
4. Set environment variable

### Option 3: Docker MongoDB
```bash
# Run MongoDB in Docker
docker run -d --name ai-influencer-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:latest

# Connection string for Docker
export MONGODB_CONNECTION_STRING="mongodb://admin:password@localhost:27017/"
```

## 📊 Database Operations

### User Management
```python
# Create user with detailed profile
user_data = {
    "username": "tech_startup",
    "email": "ceo@startup.com",
    "full_name": "Sarah Johnson",
    "business_type": "Technology",
    "target_audience": "Entrepreneurs",
    "preferred_platforms": ["LinkedIn", "Twitter"],
    "subscription_tier": "premium"
}
user_id = db.create_user(user_data)

# Get user
user = db.get_user(user_id)

# Update user
db.update_user(user_id, {"last_active": datetime.utcnow()})

# Delete user (and all related data)
db.delete_user(user_id)
```

### Persona Management
```python
# Create detailed persona
persona_data = {
    "user_id": user_id,
    "character_name": "Professional Sarah",
    "description": "Confident tech CEO for LinkedIn",
    "age_range": "35-40",
    "gender": "female",
    "profession": "Technology CEO",
    "style": "professional",
    "target_platform": "linkedin",
    "personality_traits": ["confident", "visionary"],
    "brand_voice": "Authoritative yet accessible",
    "content_themes": ["leadership", "innovation"]
}
persona_id = db.create_persona(persona_data)

# Get all user personas
personas = db.get_user_personas(user_id)
```

### Image Storage
```python
# Store image file
image_id = db.store_image(
    image_path="/path/to/image.png",
    metadata={
        "persona_id": persona_id,
        "platform": "linkedin",
        "campaign": "q1_launch"
    }
)

# Store raw image data
image_id = db.store_image_data(
    image_data=image_bytes,
    filename="generated_image.png",
    metadata={"type": "profile_image"}
)

# Retrieve image
image_data = db.get_image(image_id)
```

### Analytics
```python
# Get user analytics
analytics = db.get_user_analytics(user_id)
print(f"Total generations: {analytics['total_generations']}")
print(f"Average rating: {analytics['average_rating']}")

# Get generation history
history = db.get_generation_history(user_id, limit=10)
```

## 🔗 Integration with Image Generation

### Complete Workflow Example
```python
from database.mongodb_manager import AIInfluencerDB
from ai_services.comfyApi import ComfyUIClient

# Initialize services
db = AIInfluencerDB()
comfy = ComfyUIClient()

# Generate image
image_path = comfy.generate_image(
    prompt="Professional tech CEO headshot",
    character_description="confident, modern, approachable"
)

# Store in database
if image_path:
    # Store image
    image_id = db.store_image(image_path, {
        "persona_id": persona_id,
        "platform": "linkedin"
    })
    
    # Log generation
    generation_id = db.log_generation({
        "user_id": user_id,
        "persona_id": persona_id,
        "generation_type": "image",
        "prompt_used": "Professional tech CEO headshot",
        "file_ids": [image_id],
        "platform_optimized": "linkedin",
        "duration_seconds": 45.2,
        "user_satisfied": True
    })
```

## 🧪 Testing

### Run Tests
```bash
# Test MongoDB connection
cd src/database
python test_mongodb_simple.py

# Full integration demo
python demo_mongodb_integration.py

# Complete test suite (requires MongoDB)
python test_mongodb_connection.py
```

## 📁 File Structure
```
src/database/
├── mongodb_manager.py           # Main MongoDB integration class
├── test_mongodb_connection.py   # Comprehensive test suite
├── test_mongodb_simple.py       # Simple connection test
├── demo_mongodb_integration.py  # Full integration demo
├── setup_mongodb_env.py         # Environment setup helper
└── README.md                    # This documentation
```

## 🔒 Security Best Practices

### Connection String Security
```python
# Use environment variables
import os
connection_string = os.getenv('MONGODB_CONNECTION_STRING')

# URL encode credentials
import urllib.parse
username = urllib.parse.quote_plus("user@domain.com")
password = urllib.parse.quote_plus("pa$$word")
```

### Data Validation
- All inputs are validated before database operations
- ObjectId conversion with error handling
- Proper datetime handling with UTC
- Sanitized user inputs

## 🚀 Production Deployment

### Environment Variables
```bash
# Required
MONGODB_CONNECTION_STRING="mongodb+srv://user:pass@cluster.mongodb.net/ai_influencer"

# Optional (with defaults)
MONGODB_DATABASE_NAME="ai_influencer"
MONGODB_CONNECTION_TIMEOUT=20000
```

### Performance Optimization
- Database indexes automatically created for:
  - User email and username (unique)
  - Persona user_id and character_name
  - Generation timestamps and user_id
- GridFS for efficient image storage
- Connection pooling via PyMongo

## 📈 Analytics and Monitoring

### Available Metrics
- User generation counts
- Average generation ratings
- Platform usage statistics
- Persona performance metrics
- Storage usage analytics

### Database Health
```python
# Check database status
info = db.get_database_info()
print(f"Status: {info['status']}")
print(f"Total documents: {info['total_documents']}")
print(f"Storage size: {info['storage_size_mb']} MB")
```

## 🎯 Next Steps

1. **Set up MongoDB instance** (local, Atlas, or Docker)
2. **Configure connection string** in environment
3. **Test connection** with provided test scripts
4. **Integrate with image generation** workflows
5. **Deploy to production** with proper security

---

**Ready to store your AI influencer data persistently! 🚀**
