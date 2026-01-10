"""
Asset Agent - Manages advertising assets (images, videos)
Handles uploading, retrieving, validating, and caching assets
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

# Quiet mode flag (suppress debug output)
QUIET_MODE = False

def set_asset_quiet_mode(quiet: bool):
    """Set quiet mode globally in asset module"""
    global QUIET_MODE
    QUIET_MODE = quiet

def log_debug(msg: str):
    """Print debug message only if not in quiet mode"""
    if not QUIET_MODE:
        print(msg)


# ============================================================================
# DATA MODELS
# ============================================================================

class AssetType(str, Enum):
    """Asset types supported"""
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class ImageAsset:
    """Image asset representation"""
    image_hash: str
    filename: str
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None
    created_time: Optional[str] = None


@dataclass
class VideoAsset:
    """Video asset representation"""
    video_id: str
    filename: str
    size_bytes: int
    duration: Optional[float] = None
    status: str = "PROCESSING"  # PROCESSING, READY, FAILED
    url: Optional[str] = None
    created_time: Optional[str] = None
    thumbnail_url: Optional[str] = None


class AssetValidationError(Exception):
    """Asset validation failed"""
    pass


class AssetUploadError(Exception):
    """Asset upload failed"""
    pass


# ============================================================================
# ASSET SPECIFICATIONS
# ============================================================================

class AssetSpecs:
    """Asset specification requirements"""
    
    IMAGE_SPECS = {
        "max_size_mb": 8,
        "max_size_bytes": 8 * 1024 * 1024,
        "supported_formats": ["jpg", "jpeg", "png", "gif", "webp", "bmp"],
        "min_width": 100,
        "min_height": 100,
        "max_width": 4096,
        "max_height": 4096,
        "aspect_ratios": [1.0, 1.333, 1.5, 2.0, 0.5, 0.75]
    }
    
    VIDEO_SPECS = {
        "max_size_mb": 2048,  # 2GB
        "max_size_bytes": 2048 * 1024 * 1024,
        "supported_formats": ["mp4", "mov", "avi", "flv", "wmv", "webm"],
        "min_duration_seconds": 1,
        "max_duration_seconds": 3600,  # 1 hour
        "min_width": 100,
        "min_height": 100,
        "max_width": 4096,
        "max_height": 4096,
        "supported_framerates": [24, 25, 29.97, 30, 50, 59.94, 60]
    }
    
    @classmethod
    def validate_image(cls, filepath: str, width: Optional[int] = None, height: Optional[int] = None) -> Dict[str, Any]:
        """Validate image file against specifications"""
        specs = cls.IMAGE_SPECS
        
        # Check file exists
        if not os.path.exists(filepath):
            raise AssetValidationError(f"File not found: {filepath}")
        
        # Check file format
        ext = os.path.splitext(filepath)[1].lower().lstrip('.')
        if ext not in specs["supported_formats"]:
            raise AssetValidationError(f"Unsupported image format: {ext}. Supported: {', '.join(specs['supported_formats'])}")
        
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > specs["max_size_bytes"]:
            raise AssetValidationError(f"Image size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({specs['max_size_mb']}MB)")
        
        if file_size == 0:
            raise AssetValidationError("Image file is empty")
        
        # Validate dimensions if provided
        if width is not None and height is not None:
            if width < specs["min_width"] or height < specs["min_height"]:
                raise AssetValidationError(f"Image dimensions ({width}x{height}) below minimum ({specs['min_width']}x{specs['min_height']})")
            if width > specs["max_width"] or height > specs["max_height"]:
                raise AssetValidationError(f"Image dimensions ({width}x{height}) exceed maximum ({specs['max_width']}x{specs['max_height']})")
        
        return {
            "valid": True,
            "format": ext,
            "size_bytes": file_size,
            "width": width,
            "height": height
        }
    
    @classmethod
    def validate_video(cls, filepath: str, duration: Optional[float] = None, width: Optional[int] = None, height: Optional[int] = None) -> Dict[str, Any]:
        """Validate video file against specifications"""
        specs = cls.VIDEO_SPECS
        
        # Check file exists
        if not os.path.exists(filepath):
            raise AssetValidationError(f"File not found: {filepath}")
        
        # Check file format
        ext = os.path.splitext(filepath)[1].lower().lstrip('.')
        if ext not in specs["supported_formats"]:
            raise AssetValidationError(f"Unsupported video format: {ext}. Supported: {', '.join(specs['supported_formats'])}")
        
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > specs["max_size_bytes"]:
            raise AssetValidationError(f"Video size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({specs['max_size_mb']}MB)")
        
        if file_size == 0:
            raise AssetValidationError("Video file is empty")
        
        # Validate duration if provided
        if duration is not None:
            if duration < specs["min_duration_seconds"]:
                raise AssetValidationError(f"Video duration ({duration}s) below minimum ({specs['min_duration_seconds']}s)")
            if duration > specs["max_duration_seconds"]:
                raise AssetValidationError(f"Video duration ({duration}s) exceeds maximum ({specs['max_duration_seconds']}s)")
        
        # Validate dimensions if provided
        if width is not None and height is not None:
            if width < specs["min_width"] or height < specs["min_height"]:
                raise AssetValidationError(f"Video dimensions ({width}x{height}) below minimum ({specs['min_width']}x{specs['min_height']})")
            if width > specs["max_width"] or height > specs["max_height"]:
                raise AssetValidationError(f"Video dimensions ({width}x{height}) exceed maximum ({specs['max_width']}x{specs['max_height']})")
        
        return {
            "valid": True,
            "format": ext,
            "size_bytes": file_size,
            "duration": duration,
            "width": width,
            "height": height
        }


# ============================================================================
# ASSET CACHE
# ============================================================================

class AssetCache:
    """Cache for uploaded assets to avoid re-uploading"""
    
    def __init__(self, cache_file: str = ".asset_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log_debug(f"[AssetCache] Failed to load cache: {e}")
                return {"images": {}, "videos": {}}
        return {"images": {}, "videos": {}}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            log_debug(f"[AssetCache] Failed to save cache: {e}")
    
    def get_image(self, filepath: str) -> Optional[str]:
        """Get cached image hash"""
        return self.cache.get("images", {}).get(filepath)
    
    def set_image(self, filepath: str, image_hash: str):
        """Cache image hash"""
        if "images" not in self.cache:
            self.cache["images"] = {}
        self.cache["images"][filepath] = image_hash
        self._save_cache()
    
    def get_video(self, filepath: str) -> Optional[str]:
        """Get cached video ID"""
        return self.cache.get("videos", {}).get(filepath)
    
    def set_video(self, filepath: str, video_id: str):
        """Cache video ID"""
        if "videos" not in self.cache:
            self.cache["videos"] = {}
        self.cache["videos"][filepath] = video_id
        self._save_cache()
    
    def clear(self):
        """Clear all cache"""
        self.cache = {"images": {}, "videos": {}}
        self._save_cache()


# ============================================================================
# ASSET AGENT
# ============================================================================

class AssetAgent:
    """
    Agent for managing advertising assets (images, videos)
    Handles upload, retrieval, validation, and caching
    """
    
    def __init__(self, api_client):
        """
        Initialize Asset Agent
        
        Args:
            api_client: MetaAPIClient instance for making API calls
        """
        self.api = api_client
        self.cache = AssetCache()
        log_debug("[AssetAgent] Initialized with Asset Cache")
    
    async def upload_image(self, ad_account_id: str, filepath: str, width: Optional[int] = None, height: Optional[int] = None) -> ImageAsset:
        """
        Upload image to ad account
        
        Args:
            ad_account_id: Ad account ID
            filepath: Path to image file
            width: Image width in pixels (optional, for validation)
            height: Image height in pixels (optional, for validation)
            
        Returns:
            ImageAsset with image_hash
            
        Raises:
            AssetValidationError: If image fails validation
            AssetUploadError: If upload fails
        """
        log_debug(f"\n[AssetAgent] Uploading image: {filepath}")
        
        try:
            # Validate image specifications
            validation_result = AssetSpecs.validate_image(filepath, width, height)
            log_debug(f"[AssetAgent] ✓ Image validation passed: {validation_result['format'].upper()}, {validation_result['size_bytes'] / 1024:.2f}KB")
            
            # Check cache first
            cached_hash = self.cache.get_image(filepath)
            if cached_hash:
                log_debug(f"[AssetAgent] ✓ Using cached image hash: {cached_hash}")
                return ImageAsset(
                    image_hash=cached_hash,
                    filename=os.path.basename(filepath),
                    size_bytes=validation_result['size_bytes'],
                    width=width,
                    height=height
                )
            
            # Read image file
            with open(filepath, 'rb') as f:
                image_data = f.read()
            
            # Upload to Meta API
            endpoint = f"/act_{ad_account_id}/adimages"
            
            # Use httpx to handle multipart upload
            import httpx
            
            files = {"file": (os.path.basename(filepath), image_data)}
            params = {"access_token": self.api.access_token}
            
            log_debug(f"[AssetAgent] POST {endpoint}")
            
            response = await self.api.session.post(endpoint, files=files, params=params)
            result = self.api._handle_response(response)
            
            # Extract image hash from API response
            # Response format: {"images": {"filename.jpg": {"hash": "...", "url": "...", ...}}}
            image_hash = None
            filename = os.path.basename(filepath)
            
            if "images" in result and filename in result["images"]:
                image_hash = result["images"][filename].get("hash")
            
            if not image_hash:
                raise AssetUploadError(f"No image_hash returned from API. Response: {result}")
            
            # Cache the result
            self.cache.set_image(filepath, image_hash)
            
            log_debug(f"[AssetAgent] ✓ Image uploaded successfully: {image_hash}")
            
            return ImageAsset(
                image_hash=image_hash,
                filename=filename,
                size_bytes=validation_result['size_bytes'],
                width=width,
                height=height
            )
        
        except AssetValidationError as e:
            log_debug(f"[AssetAgent] ✗ Image validation failed: {e}")
            raise
        except Exception as e:
            log_debug(f"[AssetAgent] ✗ Image upload failed: {e}")
            raise AssetUploadError(f"Failed to upload image '{filepath}': {str(e)}") from e
    
    async def upload_video(self, ad_account_id: str, filepath: str, duration: Optional[float] = None, 
                          width: Optional[int] = None, height: Optional[int] = None, 
                          upload_phase: str = "start") -> VideoAsset:
        """
        Upload video to ad account
        
        Args:
            ad_account_id: Ad account ID
            filepath: Path to video file
            duration: Video duration in seconds (optional, for validation)
            width: Video width in pixels (optional, for validation)
            height: Video height in pixels (optional, for validation)
            upload_phase: Upload phase - 'start', 'transfer', 'finish', or 'cancel' (default: 'start')
            
        Returns:
            VideoAsset with video_id
            
        Raises:
            AssetValidationError: If video fails validation
            AssetUploadError: If upload fails
        """
        log_debug(f"\n[AssetAgent] Uploading video: {filepath}")
        
        try:
            # Validate video specifications
            validation_result = AssetSpecs.validate_video(filepath, duration, width, height)
            log_debug(f"[AssetAgent] ✓ Video validation passed: {validation_result['format'].upper()}, {validation_result['size_bytes'] / 1024 / 1024:.2f}MB")
            
            # Check cache first
            cached_video_id = self.cache.get_video(filepath)
            if cached_video_id:
                log_debug(f"[AssetAgent] ✓ Using cached video ID: {cached_video_id}")
                return VideoAsset(
                    video_id=cached_video_id,
                    filename=os.path.basename(filepath),
                    size_bytes=validation_result['size_bytes'],
                    duration=duration,
                    status="READY"
                )
            
            # Read video file
            with open(filepath, 'rb') as f:
                video_data = f.read()
            
            # Upload to Meta API
            endpoint = f"/act_{ad_account_id}/advideos"
            
            # Use httpx to handle multipart upload
            import httpx
            
            files = {"file": (os.path.basename(filepath), video_data)}
            params = {
                "access_token": self.api.access_token,
                "upload_phase": upload_phase
            }
            
            log_debug(f"[AssetAgent] POST {endpoint}")
            
            response = await self.api.session.post(endpoint, files=files, params=params)
            result = self.api._handle_response(response)
            
            video_id = result.get("video_id")
            if not video_id:
                raise AssetUploadError("No video_id returned from API")
            
            # Cache the result
            self.cache.set_video(filepath, video_id)
            
            log_debug(f"[AssetAgent] ✓ Video uploaded successfully: {video_id}")
            
            return VideoAsset(
                video_id=video_id,
                filename=os.path.basename(filepath),
                size_bytes=validation_result['size_bytes'],
                duration=duration,
                status="PROCESSING"
            )
        
        except AssetValidationError as e:
            log_debug(f"[AssetAgent] ✗ Video validation failed: {e}")
            raise
        except Exception as e:
            log_debug(f"[AssetAgent] ✗ Video upload failed: {e}")
            raise AssetUploadError(f"Failed to upload video '{filepath}': {str(e)}") from e
    
    async def get_image(self, ad_account_id: str, image_hash: str) -> Dict[str, Any]:
        """
        Get image details from ad account's image library
        
        Args:
            ad_account_id: Ad account ID
            image_hash: Image hash identifier
            
        Returns:
            Image details from API
        """
        log_debug(f"\n[AssetAgent] Retrieving image: {image_hash}")
        
        try:
            # Query the ad account's images endpoint with hashes as JSON array string
            endpoint = f"/act_{ad_account_id}/adimages"
            params = {
                "fields": "id,hash,url,created_time,width,height,name",
                "hashes": json.dumps([image_hash])  # Convert to JSON string
            }
            result = await self.api.get(endpoint, params=params)
            log_debug(f"[AssetAgent] ✓ Image retrieved: {image_hash}")
            return result
        except Exception as e:
            log_debug(f"[AssetAgent] ✗ Failed to retrieve image: {e}")
            raise
    
    async def get_video(self, ad_account_id: str, video_id: str) -> Dict[str, Any]:
        """
        Get video details from ad account's video library
        
        Args:
            ad_account_id: Ad account ID
            video_id: Video ID identifier
            
        Returns:
            Video details from API
        """
        log_debug(f"\n[AssetAgent] Retrieving video: {video_id}")
        
        try:
            # Query the ad account's videos endpoint with video_ids as JSON array string
            endpoint = f"/act_{ad_account_id}/advideos"
            params = {
                "fields": "id,video_id,url,created_time,status,thumbnail_url,length",
                "video_ids": json.dumps([video_id])  # Convert to JSON string
            }
            result = await self.api.get(endpoint, params=params)
            log_debug(f"[AssetAgent] ✓ Video retrieved: {video_id}")
            return result
        except Exception as e:
            log_debug(f"[AssetAgent] ✗ Failed to retrieve video: {e}")
            raise
    
    def clear_cache(self):
        """Clear asset cache"""
        self.cache.clear()
        log_debug("[AssetAgent] ✓ Asset cache cleared")
