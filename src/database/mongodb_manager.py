"""
MongoDB Database Manager for AI Influencer Project
Handles user data, AI personas, and generated images storage
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import base64
from io import BytesIO
import urllib.parse

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
import gridfs

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AIInfluencerDB:
    """MongoDB database manager for AI Influencer application"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the AI Influencer Database Manager.
        
        Args:
            connection_string: MongoDB connection string. If None, uses environment variable.
        """
        # Get connection string from parameter or environment
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = os.getenv(
                'MONGODB_CONNECTION_STRING',
                'mongodb+srv://AIInfluenser:AiInfluenser%40321@cluster0.czj5c04.mongodb.net/'
            )
        
        # Parse connection string to handle credentials properly
        if '@' in self.connection_string and 'mongodb://' in self.connection_string:
            # Extract and URL encode credentials if present
            parts = self.connection_string.split('@')
            if len(parts) == 2:
                protocol_and_creds = parts[0]
                host_and_params = parts[1]
                
                if '://' in protocol_and_creds:
                    protocol, creds = protocol_and_creds.split('://')
                    if ':' in creds:
                        username, password = creds.split(':')
                        username = urllib.parse.quote_plus(username)
                        password = urllib.parse.quote_plus(password)
                        self.connection_string = f"{protocol}://{username}:{password}@{host_and_params}"
        
        # Initialize MongoDB client
        self.client = MongoClient(self.connection_string)
        self.db = self.client.AiInfluensor  # Use existing AiInfluensor database (note the case)
        
        # Initialize GridFS for image storage
        self.fs = gridfs.GridFS(self.db)
        
        # Initialize collections
        self.users = self.db.users
        self.personas = self.db.personas
        self.generations = self.db.generations
        self.sessions = self.db.sessions
        
        # Create indexes for better performance
        self._create_indexes()
    
    def connect(self) -> bool:
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.ai_influencer
            self.fs = gridfs.GridFS(self.db)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Initialize collections
            self.users = self.db.users
            self.personas = self.db.personas
            self.generations = self.db.generations
            self.sessions = self.db.sessions
            
            # Create indexes for better performance
            self._create_indexes()
            
            self.connected = True
            print("✅ Connected to MongoDB successfully")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
            print("🔌 Disconnected from MongoDB")
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # User indexes
            self.users.create_index("email", unique=True)
            self.users.create_index("username", unique=True)
            
            # Persona indexes
            self.personas.create_index("user_id")
            self.personas.create_index("character_name")
            self.personas.create_index([("user_id", 1), ("character_name", 1)], unique=True)
            
            # Generation indexes
            self.generations.create_index("user_id")
            self.generations.create_index("persona_id")
            self.generations.create_index("created_at")
            self.generations.create_index("generation_type")
            
            # Session indexes
            self.sessions.create_index("user_id")
            self.sessions.create_index("created_at")
            
            print("📊 Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    # ==========================================
    # Database Information and Health
    # ==========================================
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get general database information and health status.
        
        Returns:
            Dict containing database statistics and information
        """
        try:
            # Test connection
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command('dbstats')
            
            # Get collection names
            collections = self.db.list_collection_names()
            
            # Count total documents across all collections
            total_docs = 0
            for collection_name in collections:
                try:
                    total_docs += self.db[collection_name].count_documents({})
                except:
                    pass  # Skip if collection has issues
            
            return {
                'status': 'connected',
                'database_name': self.db.name,
                'collections': collections,
                'total_documents': total_docs,
                'database_size_mb': round(stats.get('dataSize', 0) / (1024 * 1024), 2),
                'storage_size_mb': round(stats.get('storageSize', 0) / (1024 * 1024), 2),
                'indexes': stats.get('indexes', 0),
                'server_version': self.client.server_info()['version']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'database_name': None,
                'collections': [],
                'total_documents': 0
            }
    
    def test_connection(self) -> bool:
        """
        Test if MongoDB connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    # ==========================================
    # User Management
    # ==========================================
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user"""
        try:
            user_doc = {
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "full_name": user_data.get("full_name"),
                "business_type": user_data.get("business_type"),
                "target_audience": user_data.get("target_audience"),
                "preferred_platforms": user_data.get("preferred_platforms", []),
                "subscription_tier": user_data.get("subscription_tier", "free"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "total_generations": 0,
                "personas_created": 0,
                "settings": {
                    "default_style": user_data.get("default_style", "professional"),
                    "default_platform": user_data.get("default_platform", "instagram"),
                    "quality_preference": user_data.get("quality_preference", "high")
                }
            }
            
            result = self.users.insert_one(user_doc)
            print(f"✅ User created: {user_data.get('username')} (ID: {result.inserted_id})")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            return None
    
    def get_user(self, user_id: str = None, email: str = None, username: str = None) -> Optional[Dict[str, Any]]:
        """Get user by ID, email, or username"""
        try:
            query = {}
            if user_id:
                query["_id"] = ObjectId(user_id)
            elif email:
                query["email"] = email
            elif username:
                query["username"] = username
            else:
                return None
            
            user = self.users.find_one(query)
            if user:
                user["_id"] = str(user["_id"])
            return user
            
        except Exception as e:
            print(f"❌ User retrieval failed: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ User update failed: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all associated data"""
        try:
            # Delete user's personas
            self.personas.delete_many({"user_id": ObjectId(user_id)})
            
            # Delete user's generations
            self.generations.delete_many({"user_id": ObjectId(user_id)})
            
            # Delete user's sessions
            self.sessions.delete_many({"user_id": ObjectId(user_id)})
            
            # Delete the user
            result = self.users.delete_one({"_id": ObjectId(user_id)})
            
            print(f"✅ User and associated data deleted: {user_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"❌ User deletion failed: {e}")
            return False

    # ================================
    # PERSONA MANAGEMENT
    # ================================
    
    def create_persona(self, persona_data: Dict[str, Any]) -> Optional[str]:
        """Create a new AI persona"""
        try:
            persona_doc = {
                "user_id": ObjectId(persona_data["user_id"]),
                "character_name": persona_data["character_name"],
                "description": persona_data["description"],
                "age_range": persona_data.get("age_range"),
                "gender": persona_data.get("gender"),
                "profession": persona_data.get("profession"),
                "style": persona_data.get("style", "professional"),
                "target_platform": persona_data.get("target_platform", "instagram"),
                "personality_traits": persona_data.get("personality_traits", []),
                "brand_voice": persona_data.get("brand_voice"),
                "content_themes": persona_data.get("content_themes", []),
                "visual_preferences": {
                    "background_style": persona_data.get("background_style"),
                    "lighting_preference": persona_data.get("lighting_preference"),
                    "color_scheme": persona_data.get("color_scheme")
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "generation_count": 0,
                "last_generated": None,
                "status": "active"
            }
            
            result = self.personas.insert_one(persona_doc)
            
            # Update user's persona count
            self.users.update_one(
                {"_id": ObjectId(persona_data["user_id"])},
                {"$inc": {"personas_created": 1}}
            )
            
            print(f"✅ Persona created: {persona_data['character_name']} (ID: {result.inserted_id})")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Persona creation failed: {e}")
            return None
    
    def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get persona by ID"""
        try:
            persona = self.personas.find_one({"_id": ObjectId(persona_id)})
            if persona:
                persona["_id"] = str(persona["_id"])
                persona["user_id"] = str(persona["user_id"])
            return persona
            
        except Exception as e:
            print(f"❌ Persona retrieval failed: {e}")
            return None
    
    def get_user_personas(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all personas for a user"""
        try:
            personas = list(self.personas.find({"user_id": ObjectId(user_id)}))
            for persona in personas:
                persona["_id"] = str(persona["_id"])
                persona["user_id"] = str(persona["user_id"])
            return personas
            
        except Exception as e:
            print(f"❌ Personas retrieval failed: {e}")
            return []
    
    def update_persona(self, persona_id: str, update_data: Dict[str, Any]) -> bool:
        """Update persona data"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.personas.update_one(
                {"_id": ObjectId(persona_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Persona update failed: {e}")
            return False
    
    # ================================
    # IMAGE MANAGEMENT
    # ================================
    
    def store_image(self, image_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Store image file in GridFS"""
        try:
            with open(image_path, 'rb') as image_file:
                file_id = self.fs.put(
                    image_file,
                    filename=os.path.basename(image_path),
                    content_type="image/png",
                    metadata=metadata
                )
            
            print(f"✅ Image stored in GridFS: {file_id}")
            return str(file_id)
            
        except Exception as e:
            print(f"❌ Image storage failed: {e}")
            return None
    
    def store_image_data(self, image_data: bytes, filename: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Store raw image data in GridFS"""
        try:
            file_id = self.fs.put(
                image_data,
                filename=filename,
                content_type="image/png",
                metadata=metadata
            )
            
            print(f"✅ Image data stored in GridFS: {file_id}")
            return str(file_id)
            
        except Exception as e:
            print(f"❌ Image data storage failed: {e}")
            return None
    
    def get_image(self, file_id: str) -> Optional[bytes]:
        """Retrieve image from GridFS"""
        try:
            grid_out = self.fs.get(ObjectId(file_id))
            return grid_out.read()
            
        except Exception as e:
            print(f"❌ Image retrieval failed: {e}")
            return None
    
    def get_image_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get image metadata from GridFS"""
        try:
            grid_out = self.fs.get(ObjectId(file_id))
            return {
                "_id": str(grid_out._id),
                "filename": grid_out.filename,
                "content_type": grid_out.content_type,
                "length": grid_out.length,
                "upload_date": grid_out.upload_date,
                "metadata": grid_out.metadata
            }
            
        except Exception as e:
            print(f"❌ Image metadata retrieval failed: {e}")
            return None
    
    def delete_image(self, file_id: str) -> bool:
        """Delete image from GridFS"""
        try:
            self.fs.delete(ObjectId(file_id))
            print(f"✅ Image deleted from GridFS: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Image deletion failed: {e}")
            return False

    # ================================
    # GENERATION TRACKING
    # ================================
    
    def log_generation(self, generation_data: Dict[str, Any]) -> Optional[str]:
        """Log a generation session"""
        try:
            generation_doc = {
                "user_id": ObjectId(generation_data["user_id"]),
                "persona_id": ObjectId(generation_data.get("persona_id")) if generation_data.get("persona_id") else None,
                "generation_type": generation_data["generation_type"],  # 'image', 'speech', 'video'
                "prompt_used": generation_data.get("prompt_used"),
                "seed_used": generation_data.get("seed_used"),
                "settings": generation_data.get("settings", {}),
                "generation_attempts": generation_data.get("generation_attempts", 1),
                "user_satisfied": generation_data.get("user_satisfied", False),
                "feedback": generation_data.get("feedback"),
                "file_ids": generation_data.get("file_ids", []),  # GridFS file IDs
                "file_paths": generation_data.get("file_paths", []),  # Local file paths
                "duration_seconds": generation_data.get("duration_seconds"),
                "model_used": generation_data.get("model_used", "stable-diffusion-xl"),
                "platform_optimized": generation_data.get("platform_optimized"),
                "style_used": generation_data.get("style_used"),
                "created_at": datetime.utcnow(),
                "status": "completed"
            }
            
            result = self.generations.insert_one(generation_doc)
            
            # Update counters
            self.users.update_one(
                {"_id": ObjectId(generation_data["user_id"])},
                {"$inc": {"total_generations": 1}}
            )
            
            if generation_data.get("persona_id"):
                self.personas.update_one(
                    {"_id": ObjectId(generation_data["persona_id"])},
                    {
                        "$inc": {"generation_count": 1},
                        "$set": {"last_generated": datetime.utcnow()}
                    }
                )
            
            print(f"✅ Generation logged: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Generation logging failed: {e}")
            return None
    
    def get_user_generations(self, user_id: str, generation_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's generation history"""
        try:
            query = {"user_id": ObjectId(user_id)}
            if generation_type:
                query["generation_type"] = generation_type
            
            generations = list(
                self.generations.find(query)
                .sort("created_at", -1)
                .limit(limit)
            )
            
            for gen in generations:
                gen["_id"] = str(gen["_id"])
                gen["user_id"] = str(gen["user_id"])
                if gen.get("persona_id"):
                    gen["persona_id"] = str(gen["persona_id"])
            
            return generations
            
        except Exception as e:
            print(f"❌ Generations retrieval failed: {e}")
            return []
    
    def get_persona_generations(self, persona_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get generations for a specific persona"""
        try:
            generations = list(
                self.generations.find({"persona_id": ObjectId(persona_id)})
                .sort("created_at", -1)
                .limit(limit)
            )
            
            for gen in generations:
                gen["_id"] = str(gen["_id"])
                gen["user_id"] = str(gen["user_id"])
                gen["persona_id"] = str(gen["persona_id"])
            
            return generations
            
        except Exception as e:
            print(f"❌ Persona generations retrieval failed: {e}")
            return []
    
    def get_generation_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get generation history for a user"""
        try:
            generations = list(
                self.generations.find({"user_id": ObjectId(user_id)})
                .sort("created_at", -1)
                .limit(limit)
            )
            
            for gen in generations:
                gen["_id"] = str(gen["_id"])
                gen["user_id"] = str(gen["user_id"])
                if gen.get("persona_id"):
                    gen["persona_id"] = str(gen["persona_id"])
            
            return generations
            
        except Exception as e:
            print(f"❌ Generation history retrieval failed: {e}")
            return []

    # ================================
    # SESSION MANAGEMENT
    # ================================
    
    def create_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """Create a new generation session"""
        try:
            session_doc = {
                "user_id": ObjectId(session_data["user_id"]),
                "persona_id": ObjectId(session_data.get("persona_id")) if session_data.get("persona_id") else None,
                "session_type": session_data.get("session_type", "image_generation"),
                "initial_prompt": session_data.get("initial_prompt"),
                "target_platform": session_data.get("target_platform"),
                "style_preference": session_data.get("style_preference"),
                "iterations": [],
                "final_result": None,
                "user_satisfied": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            result = self.sessions.insert_one(session_doc)
            print(f"✅ Session created: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Session creation failed: {e}")
            return None
    
    def add_session_iteration(self, session_id: str, iteration_data: Dict[str, Any]) -> bool:
        """Add an iteration to a session"""
        try:
            iteration = {
                "iteration_number": iteration_data["iteration_number"],
                "prompt_used": iteration_data["prompt_used"],
                "seed_used": iteration_data.get("seed_used"),
                "generated_files": iteration_data.get("generated_files", []),
                "user_feedback": iteration_data.get("user_feedback"),
                "user_satisfied": iteration_data.get("user_satisfied", False),
                "improvements_requested": iteration_data.get("improvements_requested", []),
                "timestamp": datetime.utcnow()
            }
            
            result = self.sessions.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$push": {"iterations": iteration},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Session iteration addition failed: {e}")
            return False
    
    def complete_session(self, session_id: str, final_result: Dict[str, Any]) -> bool:
        """Mark session as completed"""
        try:
            result = self.sessions.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "final_result": final_result,
                        "user_satisfied": final_result.get("user_satisfied", False),
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Session completion failed: {e}")
            return False
    
    # ================================
    # ANALYTICS & INSIGHTS
    # ================================
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user analytics and insights"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {}
            
            # Generation statistics
            total_generations = self.generations.count_documents({"user_id": ObjectId(user_id)})
            image_generations = self.generations.count_documents({
                "user_id": ObjectId(user_id),
                "generation_type": "image"
            })
            
            # Recent activity
            recent_generations = list(
                self.generations.find({"user_id": ObjectId(user_id)})
                .sort("created_at", -1)
                .limit(10)
            )
            
            # Popular personas
            persona_stats = list(
                self.generations.aggregate([
                    {"$match": {"user_id": ObjectId(user_id), "persona_id": {"$ne": None}}},
                    {"$group": {"_id": "$persona_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ])
            )
            
            # Platform distribution
            platform_stats = list(
                self.generations.aggregate([
                    {"$match": {"user_id": ObjectId(user_id)}},
                    {"$group": {"_id": "$platform_optimized", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ])
            )
            
            return {
                "user_info": {
                    "username": user["username"],
                    "total_personas": user.get("personas_created", 0),
                    "total_generations": total_generations,
                    "member_since": user["created_at"]
                },
                "generation_stats": {
                    "total": total_generations,
                    "images": image_generations,
                    "recent_activity": len(recent_generations)
                },
                "popular_personas": persona_stats,
                "platform_distribution": platform_stats,
                "recent_generations": [
                    {
                        "id": str(gen["_id"]),
                        "type": gen["generation_type"],
                        "created_at": gen["created_at"],
                        "satisfied": gen.get("user_satisfied", False)
                    }
                    for gen in recent_generations
                ]
            }
            
        except Exception as e:
            print(f"❌ Analytics retrieval failed: {e}")
            return {}
    
    # ================================
    # UTILITY METHODS
    # ================================
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health and connection"""
        try:
            # Test connection
            self.client.admin.command('ping')
            
            # Get collection stats
            stats = {
                "connected": True,
                "database": self.db.name,
                "collections": {
                    "users": self.users.estimated_document_count(),
                    "personas": self.personas.estimated_document_count(),
                    "generations": self.generations.estimated_document_count(),
                    "sessions": self.sessions.estimated_document_count()
                },
                "gridfs_files": self.db.fs.files.estimated_document_count(),
                "last_check": datetime.utcnow()
            }
            
            return stats
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "last_check": datetime.utcnow()
            }
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old inactive sessions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = self.sessions.delete_many({
                "status": "active",
                "created_at": {"$lt": cutoff_date}
            })
            
            print(f"🧹 Cleaned up {result.deleted_count} old sessions")
            return result.deleted_count
            
        except Exception as e:
            print(f"❌ Session cleanup failed: {e}")
            return 0


# Global database instance
db_manager: Optional[AIInfluencerDB] = None


def get_db() -> AIInfluencerDB:
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None or not db_manager.connected:
        db_manager = AIInfluencerDB()
    return db_manager


def close_db():
    """Close database connection"""
    global db_manager
    if db_manager:
        db_manager.disconnect()
        db_manager = None


if __name__ == "__main__":
    # Test database connection and operations
    print("🧪 Testing MongoDB Connection and Operations")
    print("=" * 50)
    
    # Initialize database
    db = AIInfluencerDB()
    
    if not db.connected:
        print("❌ Failed to connect to database")
        exit(1)
    
    # Test health check
    health = db.health_check()
    print(f"📊 Database Health: {health}")
    
    # Test user creation
    test_user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "full_name": "Test User",
        "business_type": "Tech Startup",
        "target_audience": "Tech professionals",
        "preferred_platforms": ["instagram", "linkedin"]
    }
    
    user_id = db.create_user(test_user_data)
    if user_id:
        print(f"✅ Test user created with ID: {user_id}")
        
        # Test persona creation
        test_persona_data = {
            "user_id": user_id,
            "character_name": "TestTechGuru",
            "description": "Professional tech influencer for startup content",
            "age_range": "25-30",
            "gender": "female",
            "profession": "tech entrepreneur",
            "style": "professional",
            "target_platform": "linkedin"
        }
        
        persona_id = db.create_persona(test_persona_data)
        if persona_id:
            print(f"✅ Test persona created with ID: {persona_id}")
            
            # Test generation logging
            test_generation_data = {
                "user_id": user_id,
                "persona_id": persona_id,
                "generation_type": "image",
                "prompt_used": "professional tech entrepreneur, modern office",
                "seed_used": 12345,
                "generation_attempts": 1,
                "user_satisfied": True,
                "file_paths": ["test_image.png"]
            }
            
            generation_id = db.log_generation(test_generation_data)
            if generation_id:
                print(f"✅ Test generation logged with ID: {generation_id}")
    
    # Get analytics
    if user_id:
        analytics = db.get_user_analytics(user_id)
        print(f"📈 User analytics: {analytics}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    if user_id:
        db.users.delete_one({"_id": ObjectId(user_id)})
        if persona_id:
            db.personas.delete_one({"_id": ObjectId(persona_id)})
        if generation_id:
            db.generations.delete_one({"_id": ObjectId(generation_id)})
    
    print("✅ Database testing completed successfully!")
    db.disconnect()
