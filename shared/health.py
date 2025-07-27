"""
Enhanced health check functionality for all services
Provides comprehensive service monitoring with dependency checks
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import httpx
import os
from loguru import logger


class HealthStatus:
    """Health status constants"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DependencyCheck:
    """Dependency check result"""
    def __init__(self, name: str, status: str, response_time: Optional[float] = None, error: Optional[str] = None):
        self.name = name
        self.status = status
        self.response_time = response_time
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status
        }
        if self.response_time is not None:
            result["response_time_ms"] = round(self.response_time * 1000, 2)
        if self.error:
            result["error"] = self.error
        return result


async def check_database_health() -> DependencyCheck:
    """Check Supabase database connectivity"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Import here to avoid circular imports
        from common.supabase_client import supabase
        
        # Simple query to test database connectivity
        result = supabase.table("users").select("id").limit(1).execute()
        
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        
        if result.data is not None:
            return DependencyCheck("database", HealthStatus.HEALTHY, response_time)
        else:
            return DependencyCheck("database", HealthStatus.UNHEALTHY, response_time, "No data returned")
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return DependencyCheck("database", HealthStatus.UNHEALTHY, error=str(e))


async def check_external_service_health(service_name: str, url: str, timeout: int = 5) -> DependencyCheck:
    """Check external service health via HTTP request"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            return DependencyCheck(service_name, HealthStatus.HEALTHY, response_time)
        else:
            return DependencyCheck(
                service_name, 
                HealthStatus.UNHEALTHY, 
                response_time, 
                f"HTTP {response.status_code}"
            )
            
    except Exception as e:
        logger.error(f"{service_name} health check failed: {e}")
        return DependencyCheck(service_name, HealthStatus.UNHEALTHY, error=str(e))


async def check_openai_health() -> DependencyCheck:
    """Check OpenAI API connectivity"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return DependencyCheck("openai", HealthStatus.UNHEALTHY, error="API key not configured")
        
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            return DependencyCheck("openai", HealthStatus.HEALTHY, response_time)
        else:
            return DependencyCheck(
                "openai", 
                HealthStatus.UNHEALTHY, 
                response_time, 
                f"HTTP {response.status_code}"
            )
            
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return DependencyCheck("openai", HealthStatus.UNHEALTHY, error=str(e))


def create_health_response(
    service_name: str, 
    additional_info: Optional[Dict[str, Any]] = None,
    dependencies: Optional[List[DependencyCheck]] = None
) -> Dict[str, Any]:
    """
    Create standardized health check response for services
    
    Args:
        service_name: Name of the service (e.g., "api", "ml", "pay")
        additional_info: Optional additional information to include
        dependencies: List of dependency check results
        
    Returns:
        Standardized health response dictionary
    """
    # Determine overall service status
    overall_status = HealthStatus.HEALTHY
    
    if dependencies:
        unhealthy_deps = [dep for dep in dependencies if dep.status == HealthStatus.UNHEALTHY]
        degraded_deps = [dep for dep in dependencies if dep.status == HealthStatus.DEGRADED]
        
        if unhealthy_deps:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_deps:
            overall_status = HealthStatus.DEGRADED
    
    response = {
        "service": f"{service_name}.c0r.ai",
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": os.getenv("SERVICE_VERSION", "unknown")
    }
    
    # Add dependency status
    if dependencies:
        response["dependencies"] = {
            dep.name: dep.to_dict() for dep in dependencies
        }
    
    # Add additional info
    if additional_info:
        response.update(additional_info)
    
    return response


async def create_comprehensive_health_response(
    service_name: str,
    check_database: bool = True,
    check_external_services: Optional[Dict[str, str]] = None,
    check_openai: bool = False,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create comprehensive health check response with dependency checks
    
    Args:
        service_name: Name of the service
        check_database: Whether to check database connectivity
        check_external_services: Dict of service_name -> url to check
        check_openai: Whether to check OpenAI API
        additional_info: Additional service-specific information
        
    Returns:
        Comprehensive health response with dependency status
    """
    dependencies = []
    
    # Check database if requested
    if check_database:
        db_check = await check_database_health()
        dependencies.append(db_check)
    
    # Check external services if provided
    if check_external_services:
        for service_name_ext, url in check_external_services.items():
            service_check = await check_external_service_health(service_name_ext, url)
            dependencies.append(service_check)
    
    # Check OpenAI if requested
    if check_openai:
        openai_check = await check_openai_health()
        dependencies.append(openai_check)
    
    return create_health_response(service_name, additional_info, dependencies)