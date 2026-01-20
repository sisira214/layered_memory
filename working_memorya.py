import redis
from uuid import uuid4


# =============================================================================
# CONFIGURATION
# =============================================================================
REDIS_URL = "redis://localhost:6379"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
# =============================================================================
# PART 1: WORKING MEMORY (Redis)
# =============================================================================
# Working memory is like your mental scratchpad - it holds what you're 
# currently thinking about and expires automatically.

def working_memory_set(session_id: str, key: str, value: dict, ttl: int = 300):
    """
    Store something in working memory.
    
    Args:
        session_id: Unique session identifier
        key: What we're storing (e.g., "current_goal", "user_intent")
        value: The data to store
        ttl: Time-to-live in seconds (default 5 minutes)
    """
    redis_key = f"wm:{session_id}:{key}"
    redis_client.setex(redis_key, ttl, json.dumps(value))


def working_memory_get(session_id: str, key: str) -> dict | None:
    """Retrieve something from working memory."""
    redis_key = f"wm:{session_id}:{key}"
    data = redis_client.get(redis_key)
    return json.loads(data) if data else None


def working_memory_add_observation(session_id: str, observation: dict, max_items: int = 10):
    """
    Add an observation to the observation stream.
    Uses a Redis list to maintain ordered observations.
    """
    redis_key = f"wm:{session_id}:observations"
    observation["timestamp"] = datetime.utcnow().isoformat()
    
    redis_client.lpush(redis_key, json.dumps(observation))
    redis_client.ltrim(redis_key, 0, max_items - 1)  # Keep only recent items
    redis_client.expire(redis_key, 600)  # Expire after 10 minutes


def working_memory_get_observations(session_id: str, limit: int = 5) -> list:
    """Get recent observations."""
    redis_key = f"wm:{session_id}:observations"
    items = redis_client.lrange(redis_key, 0, limit - 1)
    return [json.loads(item) for item in items]


def working_memory_get_full_context(session_id: str) -> dict:
    """Get all working memory for a session."""
    context = {}
    
    # Get all keys for this session
    pattern = f"wm:{session_id}:*"
    for key in redis_client.scan_iter(match=pattern):
        short_key = key.split(":")[-1]
        if short_key == "observations":
            context["observations"] = working_memory_get_observations(session_id)
        else:
            context[short_key] = working_memory_get(session_id, short_key)
    
    return context


def demo_working_memory():
    """Demonstrate working memory operations."""
    print("\n" + "="*60)
    print("📝 WORKING MEMORY (Redis)")
    print("="*60)
    
    session_id = f"demo_{uuid4().hex[:8]}"
    
    # Set current goal
    working_memory_set(session_id, "current_goal", {
        "goal": "Help user analyze sales data",
        "priority": "high"
    })
    print("✓ Set current goal")
    
    # Set user intent
    working_memory_set(session_id, "user_intent", {
        "intent": "data_analysis",
        "confidence": 0.9
    })
    print("✓ Set user intent")
    
    # Add some observations
    working_memory_add_observation(session_id, {"type": "user_upload", "file": "sales.csv"})
    working_memory_add_observation(session_id, {"type": "user_question", "text": "Show me trends"})
    print("✓ Added observations")
    
    # Retrieve everything
    context = working_memory_get_full_context(session_id)
    print(f"\n📋 Full Working Memory Context:")
    print(json.dumps(context, indent=2))
    
    # Show TTL
    ttl = redis_client.ttl(f"wm:{session_id}:current_goal")
    print(f"\n⏰ TTL remaining: {ttl} seconds (auto-expires!)")