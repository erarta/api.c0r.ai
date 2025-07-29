"""
Unit tests for Circuit Breaker
"""

import pytest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from services.ml.core.reliability.circuit_breaker import (
    CircuitBreaker, 
    CircuitBreakerConfig, 
    CircuitState,
    CircuitBreakerOpenException,
    CircuitBreakerRegistry,
    circuit_breaker
)


class TestCircuitBreaker:
    """Test CircuitBreaker functionality"""
    
    @pytest.fixture
    def circuit_breaker_config(self):
        """Create CircuitBreakerConfig for testing"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,
            success_threshold=2,
            timeout=1.0
        )
    
    @pytest.fixture
    def cb(self, circuit_breaker_config):
        """Create CircuitBreaker instance for testing"""
        return CircuitBreaker("test_cb", circuit_breaker_config)
    
    def test_circuit_breaker_initialization(self, cb):
        """Test CircuitBreaker initialization"""
        assert cb.name == "test_cb"
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.total_requests == 0
        assert cb.stats.successful_requests == 0
        assert cb.stats.failed_requests == 0
    
    def test_successful_execution_closed_state(self, cb):
        """Test successful execution in CLOSED state"""
        def successful_function():
            return "success"
        
        result = cb.call(successful_function)
        
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.total_requests == 1
        assert cb.stats.successful_requests == 1
        assert cb.stats.consecutive_successes == 1
        assert cb.stats.consecutive_failures == 0
    
    def test_failed_execution_closed_state(self, cb):
        """Test failed execution in CLOSED state"""
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            cb.call(failing_function)
        
        assert cb.state == CircuitState.CLOSED  # Still closed after 1 failure
        assert cb.stats.total_requests == 1
        assert cb.stats.failed_requests == 1
        assert cb.stats.consecutive_failures == 1
        assert cb.stats.consecutive_successes == 0
    
    def test_circuit_breaker_opens_after_threshold(self, cb):
        """Test circuit breaker opens after failure threshold"""
        def failing_function():
            raise ValueError("Test error")
        
        # Execute failing function multiple times to reach threshold
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_function)
        
        # Circuit breaker should now be OPEN
        assert cb.state == CircuitState.OPEN
        assert cb.stats.consecutive_failures == 3
    
    def test_circuit_breaker_rejects_requests_when_open(self, cb):
        """Test circuit breaker rejects requests when OPEN"""
        # Force circuit breaker to OPEN state
        cb.force_open()
        
        def any_function():
            return "should not execute"
        
        # Should raise CircuitBreakerOpenException
        with pytest.raises(CircuitBreakerOpenException):
            cb.call(any_function)
        
        assert cb.stats.total_requests == 1  # Request was counted but rejected
    
    def test_circuit_breaker_half_open_transition(self, cb):
        """Test transition from OPEN to HALF_OPEN"""
        # Force to OPEN state
        cb.force_open()
        cb.stats.last_failure_time = time.time() - 10  # 10 seconds ago
        
        def successful_function():
            return "success"
        
        # Should transition to HALF_OPEN and execute
        result = cb.call(successful_function)
        
        assert result == "success"
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_circuit_breaker_closes_after_success_threshold(self, cb):
        """Test circuit breaker closes after success threshold in HALF_OPEN"""
        # Set to HALF_OPEN state
        cb._move_to_half_open()
        
        def successful_function():
            return "success"
        
        # Execute successful function to reach success threshold
        for i in range(2):  # success_threshold = 2
            result = cb.call(successful_function)
            assert result == "success"
        
        # Should now be CLOSED
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.consecutive_successes == 2
    
    def test_circuit_breaker_reopens_on_failure_in_half_open(self, cb):
        """Test circuit breaker reopens on failure in HALF_OPEN state"""
        # Set to HALF_OPEN state
        cb._move_to_half_open()
        
        def failing_function():
            raise ValueError("Test error")
        
        # Single failure in HALF_OPEN should reopen circuit breaker
        with pytest.raises(ValueError):
            cb.call(failing_function)
        
        assert cb.state == CircuitState.OPEN
    
    def test_circuit_breaker_decorator(self, circuit_breaker_config):
        """Test circuit breaker as decorator"""
        cb = CircuitBreaker("decorator_test", circuit_breaker_config)
        
        @cb
        def decorated_function(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        # Test successful execution
        result = decorated_function(5)
        assert result == 10
        
        # Test failed execution
        with pytest.raises(ValueError):
            decorated_function(-1)
        
        assert cb.stats.total_requests == 2
        assert cb.stats.successful_requests == 1
        assert cb.stats.failed_requests == 1
    
    def test_circuit_breaker_timeout(self):
        """Test circuit breaker timeout functionality"""
        config = CircuitBreakerConfig(timeout=0.1)  # Very short timeout
        cb = CircuitBreaker("timeout_test", config)
        
        def slow_function():
            time.sleep(0.2)  # Longer than timeout
            return "should not complete"
        
        # Should raise TimeoutError (on Unix systems)
        if hasattr(os, 'name') and os.name != 'nt':  # Not Windows
            with pytest.raises(TimeoutError):
                cb.call(slow_function)
        else:
            # On Windows, timeout is not implemented, so function should complete
            result = cb.call(slow_function)
            assert result == "should not complete"
    
    def test_circuit_breaker_reset(self, cb):
        """Test manual circuit breaker reset"""
        # Force some failures
        def failing_function():
            raise ValueError("Test error")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_function)
        
        assert cb.state == CircuitState.OPEN
        
        # Reset circuit breaker
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.consecutive_failures == 0
        assert cb.stats.consecutive_successes == 0
    
    def test_circuit_breaker_stats(self, cb):
        """Test circuit breaker statistics"""
        def successful_function():
            return "success"
        
        def failing_function():
            raise ValueError("Test error")
        
        # Execute some functions
        cb.call(successful_function)
        cb.call(successful_function)
        
        try:
            cb.call(failing_function)
        except ValueError:
            pass
        
        stats = cb.get_stats()
        
        assert stats["name"] == "test_cb"
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["total_requests"] == 3
        assert stats["successful_requests"] == 2
        assert stats["failed_requests"] == 1
        assert stats["success_rate"] == 66.67  # 2/3 * 100
    
    def test_circuit_breaker_concurrent_access(self, cb):
        """Test circuit breaker with concurrent access"""
        results = []
        errors = []
        
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Concurrent test error")
            return "concurrent_success"
        
        def worker(should_fail=False):
            try:
                result = cb.call(test_function, should_fail)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(10):
            should_fail = i % 3 == 0  # Every 3rd request fails
            thread = threading.Thread(target=worker, args=(should_fail,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) + len(errors) == 10
        assert cb.stats.total_requests == 10
    
    def test_circuit_breaker_recovery_timeout_check(self, cb):
        """Test recovery timeout check"""
        # Force to OPEN state
        cb.force_open()
        cb.stats.last_failure_time = time.time() - 1  # 1 second ago
        
        # Should not attempt reset (recovery_timeout = 5 seconds)
        assert not cb._should_attempt_reset()
        
        # Set failure time to more than recovery_timeout ago
        cb.stats.last_failure_time = time.time() - 10  # 10 seconds ago
        
        # Should attempt reset now
        assert cb._should_attempt_reset()
    
    def test_circuit_breaker_expected_exceptions(self):
        """Test circuit breaker with specific expected exceptions"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            expected_exception=(ValueError, TypeError)
        )
        cb = CircuitBreaker("exception_test", config)
        
        def function_with_value_error():
            raise ValueError("Expected error")
        
        def function_with_runtime_error():
            raise RuntimeError("Unexpected error")
        
        # ValueError should be handled as expected
        with pytest.raises(ValueError):
            cb.call(function_with_value_error)
        
        assert cb.stats.failed_requests == 1
        
        # RuntimeError should also be handled (it's a subclass of Exception)
        with pytest.raises(RuntimeError):
            cb.call(function_with_runtime_error)
        
        assert cb.stats.failed_requests == 2


class TestCircuitBreakerRegistry:
    """Test CircuitBreakerRegistry functionality"""
    
    @pytest.fixture
    def registry(self):
        """Create CircuitBreakerRegistry for testing"""
        return CircuitBreakerRegistry()
    
    def test_registry_initialization(self, registry):
        """Test registry initialization"""
        assert len(registry._breakers) == 0
    
    def test_get_or_create_new_breaker(self, registry):
        """Test creating new circuit breaker through registry"""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = registry.get_or_create("test_breaker", config)
        
        assert cb.name == "test_breaker"
        assert cb.config.failure_threshold == 5
        assert "test_breaker" in registry._breakers
    
    def test_get_or_create_existing_breaker(self, registry):
        """Test getting existing circuit breaker from registry"""
        config1 = CircuitBreakerConfig(failure_threshold=3)
        config2 = CircuitBreakerConfig(failure_threshold=5)
        
        # Create first breaker
        cb1 = registry.get_or_create("test_breaker", config1)
        
        # Get same breaker (config2 should be ignored)
        cb2 = registry.get_or_create("test_breaker", config2)
        
        assert cb1 is cb2
        assert cb1.config.failure_threshold == 3  # Original config preserved
    
    def test_registry_get_nonexistent(self, registry):
        """Test getting non-existent circuit breaker"""
        cb = registry.get("nonexistent")
        assert cb is None
    
    def test_registry_get_all_stats(self, registry):
        """Test getting all stats from registry"""
        # Create some breakers
        cb1 = registry.get_or_create("breaker1")
        cb2 = registry.get_or_create("breaker2")
        
        # Execute some operations
        cb1.call(lambda: "success")
        cb2.call(lambda: "success")
        
        stats = registry.get_all_stats()
        
        assert "breaker1" in stats
        assert "breaker2" in stats
        assert stats["breaker1"]["total_requests"] == 1
        assert stats["breaker2"]["total_requests"] == 1
    
    def test_registry_reset_all(self, registry):
        """Test resetting all circuit breakers"""
        # Create breakers and force them to OPEN
        cb1 = registry.get_or_create("breaker1")
        cb2 = registry.get_or_create("breaker2")
        
        cb1.force_open()
        cb2.force_open()
        
        assert cb1.state == CircuitState.OPEN
        assert cb2.state == CircuitState.OPEN
        
        # Reset all
        registry.reset_all()
        
        assert cb1.state == CircuitState.CLOSED
        assert cb2.state == CircuitState.CLOSED
    
    def test_registry_remove(self, registry):
        """Test removing circuit breaker from registry"""
        cb = registry.get_or_create("test_breaker")
        assert "test_breaker" in registry._breakers
        
        # Remove breaker
        result = registry.remove("test_breaker")
        assert result is True
        assert "test_breaker" not in registry._breakers
        
        # Try to remove non-existent breaker
        result = registry.remove("nonexistent")
        assert result is False
    
    def test_registry_list_names(self, registry):
        """Test listing circuit breaker names"""
        registry.get_or_create("breaker1")
        registry.get_or_create("breaker2")
        registry.get_or_create("breaker3")
        
        names = registry.list_names()
        
        assert len(names) == 3
        assert "breaker1" in names
        assert "breaker2" in names
        assert "breaker3" in names


class TestCircuitBreakerDecorator:
    """Test circuit breaker decorator functionality"""
    
    def test_circuit_breaker_decorator_function(self):
        """Test circuit breaker decorator"""
        config = CircuitBreakerConfig(failure_threshold=2)
        
        @circuit_breaker("decorator_test", config)
        def test_function(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        # Test successful execution
        result = test_function(5)
        assert result == 10
        
        # Test failed executions
        with pytest.raises(ValueError):
            test_function(-1)
        
        with pytest.raises(ValueError):
            test_function(-2)
        
        # Circuit breaker should now be OPEN
        with pytest.raises(CircuitBreakerOpenException):
            test_function(10)  # This should be rejected
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata"""
        @circuit_breaker("metadata_test")
        def documented_function(x):
            """This function has documentation."""
            return x
        
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This function has documentation."
    
    def test_multiple_decorators_same_name(self):
        """Test multiple functions with same circuit breaker name"""
        @circuit_breaker("shared_breaker")
        def function1():
            return "function1"
        
        @circuit_breaker("shared_breaker")
        def function2():
            raise ValueError("function2 error")
        
        # Both functions should share the same circuit breaker
        result1 = function1()
        assert result1 == "function1"
        
        # Cause failures in function2
        for _ in range(3):  # Default failure threshold
            try:
                function2()
            except ValueError:
                pass
        
        # Now both functions should be affected by the open circuit breaker
        with pytest.raises(CircuitBreakerOpenException):
            function1()  # Should be rejected even though function1 itself doesn't fail


if __name__ == "__main__":
    pytest.main([__file__])