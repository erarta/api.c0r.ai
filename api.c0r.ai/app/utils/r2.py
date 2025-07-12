"""
Cloudflare R2 utility functions for photo storage

Note: For public photo access, you need to:
1. Set up Custom Domain for R2 bucket OR
2. Configure bucket policy for public read access

Current implementation assumes private bucket with signed URLs capability.
"""
import os
import uuid
import hashlib
import mimetypes
from typing import BinaryIO, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

# R2 configuration from environment
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID") 
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")

# Validate R2 configuration
if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME]):
    logger.warning("R2 credentials not fully configured. Photo upload will be disabled.")
    R2_ENABLED = False
else:
    R2_ENABLED = True
    logger.info(f"R2 configured: bucket={R2_BUCKET_NAME}")

# Create R2 client (compatible with S3 API)
def get_r2_client():
    """Create and return R2 client using S3-compatible API"""
    if not R2_ENABLED:
        raise Exception("R2 not configured")
    
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )

def generate_photo_filename(user_id: str, file_extension: str = "jpg") -> str:
    """
    Generate unique filename for photo
    
    Args:
        user_id: User UUID
        file_extension: File extension (default: jpg)
        
    Returns:
        Unique filename in format: user_id/YYYY/MM/DD/uuid.ext
    """
    from datetime import datetime
    
    # Create date-based path under user folder
    now = datetime.now()
    date_path = now.strftime("%Y/%m/%d")
    
    # Generate unique identifier
    photo_uuid = str(uuid.uuid4())
    
    # Create filename: user_id/2025/01/20/uuid.jpg
    filename = f"{user_id}/{date_path}/{photo_uuid}.{file_extension}"
    
    logger.info(f"Generated photo filename: {filename}")
    return filename

def validate_photo_file(file_data: bytes, max_size_mb: int = 10) -> tuple[bool, str]:
    """
    Validate photo file data
    
    Args:
        file_data: Binary file data
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    file_size_mb = len(file_data) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
    
    # Check if it's actually an image by reading file headers
    if not file_data:
        return False, "Empty file"
    
    # Check for common image file signatures
    image_signatures = {
        b'\xff\xd8\xff': 'jpg',
        b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'png',
        b'\x47\x49\x46\x38': 'gif',
        b'\x42\x4d': 'bmp',
        b'\x52\x49\x46\x46': 'webp'  # RIFF for WebP
    }
    
    file_header = file_data[:12]  # Read first 12 bytes
    is_image = False
    detected_format = None
    
    for signature, format_name in image_signatures.items():
        if file_header.startswith(signature):
            is_image = True
            detected_format = format_name
            break
    
    if not is_image:
        return False, "File is not a valid image format"
    
    logger.info(f"File validation passed: {detected_format}, {file_size_mb:.1f}MB")
    return True, f"Valid {detected_format} image"

async def upload_photo_to_r2(photo_data: bytes, user_id: str, content_type: str = "image/jpeg") -> Optional[str]:
    """
    Upload photo to Cloudflare R2 with validation
    
    Args:
        photo_data: Photo binary data
        user_id: User UUID
        content_type: MIME type of the photo
        
    Returns:
        Signed URL of uploaded photo or None if failed
    """
    if not R2_ENABLED:
        logger.warning("R2 not enabled, skipping photo upload")
        return None
    
    try:
        # Validate photo file
        is_valid, message = validate_photo_file(photo_data)
        if not is_valid:
            logger.error(f"Photo validation failed for user {user_id}: {message}")
            return None
        
        # Generate filename
        file_extension = "jpg" if "jpeg" in content_type else "png"
        filename = generate_photo_filename(user_id, file_extension)
        
        # Create R2 client
        r2_client = get_r2_client()
        
        # Calculate file hash for integrity
        file_hash = hashlib.md5(photo_data).hexdigest()
        
        # Upload to R2
        logger.info(f"Uploading photo to R2: {filename} (size: {len(photo_data)} bytes)")
        
        r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename,
            Body=photo_data,
            ContentType=content_type,
            Metadata={
                'user_id': user_id,
                'upload_source': 'telegram_bot',
                'file_hash': file_hash
            }
        )
        
        # Generate signed URL for private bucket access (valid for 24 hours)
        signed_url = r2_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': R2_BUCKET_NAME, 'Key': filename},
            ExpiresIn=86400  # 24 hours
        )
        
        logger.info(f"Photo uploaded successfully: {filename}")
        return signed_url
        
    except NoCredentialsError:
        logger.error("R2 credentials not found")
        return None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"R2 upload error {error_code}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error uploading to R2: {e}")
        return None

async def upload_telegram_photo(bot, photo, user_id: str) -> Optional[str]:
    """
    Upload Telegram photo to R2
    
    Args:
        bot: Telegram bot instance
        photo: Telegram photo object
        user_id: User UUID
        
    Returns:
        Public URL of uploaded photo or None if failed
    """
    try:
        logger.info(f"Starting R2 upload for user {user_id}, R2_ENABLED={R2_ENABLED}")
        
        if not R2_ENABLED:
            logger.warning(f"R2 is disabled for user {user_id}, skipping upload")
            return None
        
        # Get file info
        file = await bot.get_file(photo.file_id)
        logger.info(f"Got Telegram file for user {user_id}: {file.file_path}, size: {file.file_size}")
        
        # Download photo data
        photo_data = await bot.download_file(file.file_path)
        logger.info(f"Downloaded photo data for user {user_id}, size: {len(photo_data)} bytes")
        
        # Upload to R2
        url = await upload_photo_to_r2(photo_data, user_id, "image/jpeg")
        
        if url:
            logger.info(f"✅ R2 upload SUCCESS for user {user_id}: {url}")
        else:
            logger.warning(f"❌ R2 upload FAILED for user {user_id}")
        
        return url
        
    except Exception as e:
        logger.error(f"❌ EXCEPTION in R2 upload for user {user_id}: {e}")
        return None

def generate_signed_url(filename: str, expires_in: int = 86400) -> Optional[str]:
    """
    Generate signed URL for accessing photo in R2
    
    Args:
        filename: Photo filename/key in R2
        expires_in: URL expiration time in seconds (default: 24 hours)
        
    Returns:
        Signed URL or None if failed
    """
    if not R2_ENABLED:
        return None
    
    try:
        r2_client = get_r2_client()
        
        signed_url = r2_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': R2_BUCKET_NAME, 'Key': filename},
            ExpiresIn=expires_in
        )
        
        return signed_url
        
    except Exception as e:
        logger.error(f"Error generating signed URL for {filename}: {e}")
        return None

def get_photo_stats() -> dict:
    """
    Get statistics about photos in R2 bucket
    
    Returns:
        Dictionary with photo statistics
    """
    if not R2_ENABLED:
        return {"error": "R2 not enabled"}
    
    try:
        r2_client = get_r2_client()
        
        # List all objects in bucket (photos are now stored under user_id/)
        response = r2_client.list_objects_v2(Bucket=R2_BUCKET_NAME)
        
        if 'Contents' not in response:
            return {"total_photos": 0, "total_size": 0, "total_users": 0}
        
        photos = response['Contents']
        total_photos = len(photos)
        total_size = sum(obj['Size'] for obj in photos)
        
        # Count unique users (extract user_id from path)
        users = set()
        for photo in photos:
            key = photo['Key']
            # Extract user_id (first part before /)
            if '/' in key:
                user_id = key.split('/')[0]
                # Check if it looks like a UUID (basic check)
                if len(user_id) > 10:  # UUIDs are longer than 10 chars
                    users.add(user_id)
        
        return {
            "total_photos": total_photos,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_users": len(users),
            "avg_photos_per_user": round(total_photos / len(users), 1) if users else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting photo stats: {e}")
        return {"error": str(e)}

async def get_user_photos(user_id: str, limit: int = 50) -> list:
    """
    Get photos for specific user
    
    Args:
        user_id: User UUID
        limit: Maximum number of photos to return
        
    Returns:
        List of photo information
    """
    if not R2_ENABLED:
        return []
    
    try:
        r2_client = get_r2_client()
        
        # List objects with user_id prefix
        response = r2_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix=f"{user_id}/",
            MaxKeys=limit
        )
        
        if 'Contents' not in response:
            return []
        
        photos = []
        for obj in response['Contents']:
            # Generate signed URL for each photo
            signed_url = generate_signed_url(obj['Key'])
            
            photos.append({
                'filename': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'url': signed_url
            })
        
        # Sort by last modified (newest first)
        photos.sort(key=lambda x: x['last_modified'], reverse=True)
        
        return photos
        
    except Exception as e:
        logger.error(f"Error getting photos for user {user_id}: {e}")
        return []

# Test function for R2 connection
async def test_r2_connection() -> bool:
    """
    Test R2 connection and bucket access
    
    Returns:
        True if connection successful, False otherwise
    """
    if not R2_ENABLED:
        logger.warning("R2 not enabled, skipping connection test")
        return False
    
    try:
        r2_client = get_r2_client()
        
        # Try to list bucket contents (just first item)
        response = r2_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            MaxKeys=1
        )
        
        logger.info("R2 connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"R2 connection test failed: {e}")
        return False 