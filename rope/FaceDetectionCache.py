"""
Face Detection Cache Module

This module provides a thread-safe cache for face detection results to enable
frame lookahead and reduce redundant computations.
"""

import threading
from collections import OrderedDict
from typing import Dict, Tuple, List, Optional, Any
import time
import numpy as np


class FaceDetectionResult:
    """Container for face detection results"""
    def __init__(self, 
                 bboxes: List[np.ndarray], 
                 kpss_5: List[np.ndarray], 
                 kpss: List[np.ndarray],
                 embeddings: Optional[List[np.ndarray]] = None,
                 timestamp: Optional[float] = None):
        self.bboxes = bboxes
        self.kpss_5 = kpss_5  # 5-point facial landmarks
        self.kpss = kpss      # Extended landmarks (68, 98, etc.)
        self.embeddings = embeddings or []
        self.timestamp = timestamp or time.time()
        
    def is_valid(self, max_age: float = 300.0) -> bool:
        """Check if cache entry is still valid based on age"""
        return (time.time() - self.timestamp) < max_age


class FaceDetectionCache:
    """
    Thread-safe LRU cache for face detection results.
    
    This cache stores face detection results indexed by frame number,
    enabling lookahead processing and reducing redundant computations.
    """
    
    def __init__(self, max_frames: int = 60, max_age: float = 300.0):
        """
        Initialize the cache.
        
        Args:
            max_frames: Maximum number of frames to cache
            max_age: Maximum age of cache entries in seconds
        """
        self.max_frames = max_frames
        self.max_age = max_age
        self._cache: OrderedDict[int, FaceDetectionResult] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
    def get(self, frame_id: int) -> Optional[FaceDetectionResult]:
        """
        Retrieve detection results for a frame.
        
        Args:
            frame_id: Frame number
            
        Returns:
            FaceDetectionResult if found and valid, None otherwise
        """
        with self._lock:
            if frame_id in self._cache:
                result = self._cache[frame_id]
                if result.is_valid(self.max_age):
                    # Move to end (most recently used)
                    self._cache.move_to_end(frame_id)
                    self._hits += 1
                    return result
                else:
                    # Expired entry
                    del self._cache[frame_id]
            
            self._misses += 1
            return None
    
    def put(self, frame_id: int, result: FaceDetectionResult) -> None:
        """
        Store detection results for a frame.
        
        Args:
            frame_id: Frame number
            result: Detection results to cache
        """
        with self._lock:
            # Remove existing entry if present
            if frame_id in self._cache:
                del self._cache[frame_id]
            
            # Add new entry
            self._cache[frame_id] = result
            
            # Evict oldest if over capacity
            while len(self._cache) > self.max_frames:
                self._evict_oldest()
    
    def _evict_oldest(self) -> None:
        """Evict the least recently used entry"""
        if self._cache:
            self._cache.popitem(last=False)
            self._evictions += 1
    
    def clear(self) -> None:
        """Clear all cached entries"""
        with self._lock:
            self._cache.clear()
            self._reset_stats()
    
    def _reset_stats(self) -> None:
        """Reset cache statistics"""
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_frames,
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }
    
    def get_cached_frames(self) -> List[int]:
        """
        Get list of currently cached frame IDs.
        
        Returns:
            List of frame IDs in cache
        """
        with self._lock:
            return list(self._cache.keys())
    
    def invalidate(self, frame_id: int) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            frame_id: Frame number to invalidate
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        with self._lock:
            if frame_id in self._cache:
                del self._cache[frame_id]
                return True
            return False
    
    def invalidate_range(self, start_frame: int, end_frame: int) -> int:
        """
        Invalidate a range of frames.
        
        Args:
            start_frame: First frame to invalidate (inclusive)
            end_frame: Last frame to invalidate (inclusive)
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            invalidated = 0
            frames_to_remove = [
                fid for fid in self._cache.keys() 
                if start_frame <= fid <= end_frame
            ]
            
            for frame_id in frames_to_remove:
                del self._cache[frame_id]
                invalidated += 1
                
            return invalidated
    
    def resize(self, new_max_frames: int) -> None:
        """
        Resize the cache capacity.
        
        Args:
            new_max_frames: New maximum number of frames to cache
        """
        with self._lock:
            self.max_frames = new_max_frames
            while len(self._cache) > self.max_frames:
                self._evict_oldest()
    
    def __len__(self) -> int:
        """Return current cache size"""
        return len(self._cache)
    
    def __contains__(self, frame_id: int) -> bool:
        """Check if frame is in cache (may be expired)"""
        return frame_id in self._cache