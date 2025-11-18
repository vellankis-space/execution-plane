# Real-Time Model Fetching Implementation

## Overview
Implemented a flexible system where users can view default models for all providers without API keys, and optionally fetch real-time models by entering provider-specific API keys.

## Features Implemented

### 1. Default Model Display (No API Key Required)
- Users can immediately see comprehensive model lists for all providers
- No setup or configuration needed
- Works out-of-the-box

### 2. Optional Real-Time Model Fetching
- Users can click "Show" to reveal API key input
- Enter provider-specific API key
- Click "Fetch Latest Models" to get real-time models from provider APIs
- Success feedback with toast notification

### 3. Visual Indicators
- **"Default List"** badge: Shown when using static fallback models
- **"Live API"** badge: Shown when models were fetched from provider API
- **"✓ Using API"** indicator in the fetch section

### 4. Two Separate API Keys
- **Provider API Key**: Used only to fetch available models (optional)
- **Agent Execution API Key**: Used by the agent to make actual API calls (required for execution)

## User Interface Changes

### Agent Playground - Model Section
Located in the Model configuration card:

```
┌─────────────────────────────────────────┐
│ Model                                    │
├─────────────────────────────────────────┤
│ Provider: [Anthropic ▼]                 │
│ Model: [claude-sonnet-4-5 ▼] Default List│
│ Temperature: 0.7 [════●════]            │
├─────────────────────────────────────────┤
│ 🔄 Fetch Real-Time Models  [Show/Hide]  │
│                                          │
│ [When expanded:]                         │
│ ┌─────────────────────────────────────┐ │
│ │ Enter anthropic API key (optional)  │ │
│ │ [Fetch Latest Models Button]        │ │
│ │ Enter your API key to fetch the     │ │
│ │ latest available models from...     │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 🔑 API Key (for agent execution)        │
│ [sk-...                              ]  │
│ This key will be used by the agent      │
│ to make API calls                        │
└─────────────────────────────────────────┘
```

## Backend Implementation

### API Endpoint: `/api/v1/models/{provider}`

**Query Parameters:**
- `api_key` (optional): Provider-specific API key for fetching real-time models

**Behavior:**
1. If `api_key` provided and valid: Fetch from provider API
2. If `api_key` missing or invalid: Return static fallback list
3. If API call fails: Return static fallback list

### Supported Providers with Real-Time Fetching

| Provider   | API Endpoint                                    | Auth Method       |
|------------|-------------------------------------------------|-------------------|
| OpenAI     | https://api.openai.com/v1/models                | Bearer Token      |
| Anthropic  | https://api.anthropic.com/v1/models             | x-api-key Header  |
| Groq       | https://api.groq.com/openai/v1/models           | Bearer Token      |
| Google     | https://generativelanguage.googleapis.com/v1/models | Query Parameter |
| OpenRouter | https://openrouter.ai/api/v1/models             | No Auth Required  |
| Together   | https://api.together.xyz/v1/models              | Bearer Token      |
| Fireworks  | https://api.fireworks.ai/inference/v1/models    | Bearer Token      |
| Cohere     | https://api.cohere.ai/v1/models                 | Bearer Token      |
| Mistral    | https://api.mistral.ai/v1/models                | Bearer Token      |

### Response Parsing
Each provider's response format is correctly parsed:
- OpenAI/Groq: Filters for chat models (gpt-*, o1-*)
- Google: Removes "models/" prefix, filters for Gemini
- OpenRouter: Returns top 20 models
- Together: Filters for instruction-tuned models
- Fireworks: Excludes embedding/vision models
- Cohere/Mistral: Returns all available models

## User Workflows

### Workflow 1: Quick Start (No API Key)
1. User opens Agent Playground
2. Selects a provider (e.g., "OpenAI")
3. Immediately sees default models (gpt-4o, gpt-4o-mini, etc.)
4. Selects a model and continues building agent
5. **No API key required for model browsing**

### Workflow 2: Real-Time Models (With API Key)
1. User opens Agent Playground
2. Selects a provider (e.g., "Anthropic")
3. Sees default models with "Default List" badge
4. Clicks "Show" in "Fetch Real-Time Models" section
5. Enters their Anthropic API key
6. Clicks "Fetch Latest Models"
7. System fetches from Anthropic API
8. Models update with "Live API" badge
9. Toast notification confirms success
10. Latest models now available for selection

### Workflow 3: Provider Switch
1. User has fetched real-time models for Provider A
2. Switches to Provider B
3. System automatically:
   - Clears previous API key
   - Resets to default models for Provider B
   - Hides the API key input
   - Shows "Default List" badge

## Error Handling

### API Key Invalid or Expired
- Shows error toast: "Failed to fetch models with provided API key"
- Falls back to default model list
- User can try again with correct key

### Network Issues
- Shows error toast: "Failed to connect to API"
- Falls back to default model list
- User can retry when connection restored

### No API Response
- Silently falls back to default models
- No disruption to user experience

## Benefits

✅ **Zero Friction**: Users can start immediately without any setup
✅ **Optional Enhancement**: Power users can fetch latest models
✅ **Clear Visual Feedback**: Badges show model source (Default vs Live API)
✅ **Graceful Degradation**: Always falls back to working defaults
✅ **Security**: API keys only sent when explicitly requested
✅ **Separation of Concerns**: Two separate API keys for different purposes
✅ **Provider Agnostic**: Works consistently across all providers

## Technical Details

### Frontend State Management
```typescript
const [availableModels, setAvailableModels] = useState<string[]>([]);
const [loadingModels, setLoadingModels] = useState(false);
const [providerApiKey, setProviderApiKey] = useState<string>("");
const [isUsingApiKey, setIsUsingApiKey] = useState(false);
const [showApiKeyInput, setShowApiKeyInput] = useState(false);
```

### Fetch Function
```typescript
const fetchModels = async (useApiKey: boolean = false) => {
  let url = `http://localhost:8000/api/v1/models/${llmProvider}`;
  if (useApiKey && providerApiKey) {
    url += `?api_key=${encodeURIComponent(providerApiKey)}`;
  }
  // Fetch and update state
}
```

### Backend Fallback Strategy
```python
async def fetch_models_from_provider(provider: str, api_key: Optional[str] = None):
    fallback_models = FALLBACK_MODELS.get(provider, [])
    
    if not api_key:
        return fallback_models  # Return defaults immediately
    
    try:
        # Attempt API call with key
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return parsed_models
        return fallback_models  # Fallback on error
    except Exception:
        return fallback_models  # Always return something
```

## Testing Scenarios

### Test 1: Default Models
1. Open Agent Playground
2. Select any provider
3. Verify models appear immediately
4. Verify "Default List" badge shows

### Test 2: Real-Time Fetch
1. Select a provider (e.g., OpenAI)
2. Click "Show" in Fetch section
3. Enter valid API key
4. Click "Fetch Latest Models"
5. Verify loading state
6. Verify success toast
7. Verify "Live API" badge shows
8. Verify models updated

### Test 3: Invalid API Key
1. Enter invalid API key
2. Click "Fetch Latest Models"
3. Verify error toast
4. Verify fallback to default models
5. Verify "Default List" badge shows

### Test 4: Provider Switch
1. Fetch real-time models for Provider A
2. Switch to Provider B
3. Verify API key input hidden
4. Verify default models shown for Provider B
5. Verify state properly reset

## Files Modified

### Frontend
- `/Users/apple/Desktop/execution-plane/frontend/src/components/AgentBuilder.tsx`
  - Added state for provider API key and UI controls
  - Created fetchModels function with optional API key parameter
  - Added collapsible UI section for real-time model fetching
  - Added visual badges for model source indication
  - Separated provider API key from agent execution API key

### Backend
- `/Users/apple/Desktop/execution-plane/backend/api/v1/models.py`
  - Implemented fetch_models_from_provider function
  - Added provider-specific API endpoints and authentication
  - Implemented response parsing for each provider
  - Added comprehensive fallback system
  - Updated endpoint to accept optional api_key parameter

### Backend Router
- `/Users/apple/Desktop/execution-plane/backend/api/v1/__init__.py`
  - Added models router to API

## Future Enhancements

1. **Cache Real-Time Models**: Store fetched models in localStorage to reduce API calls
2. **Model Metadata**: Show additional info (context length, pricing, capabilities)
3. **Batch Fetch**: Option to fetch models for all providers at once
4. **API Key Storage**: Securely store API keys in browser (encrypted)
5. **Model Search**: Add search/filter functionality for large model lists
6. **Model Comparison**: Side-by-side comparison of model capabilities

## Conclusion

The implementation successfully provides a flexible, user-friendly system that:
- Works immediately without configuration
- Offers optional real-time updates
- Maintains security and separation of concerns
- Provides clear visual feedback
- Handles errors gracefully
- Scales to support all major LLM providers
