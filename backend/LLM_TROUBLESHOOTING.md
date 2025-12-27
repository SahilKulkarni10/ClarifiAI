# LLM Troubleshooting Guide

## Common Issues and Solutions

### Issue: "Ollama timeout after 20s/30s - falling back"

**Symptoms:**
```
ERROR | Ollama timeout after 30.0s - model may be overloaded
WARNING | Ollama failed, trying Gemini...
WARNING | Gemini failed, using fallback...
```

**Causes:**
1. Ollama model is slow or overloaded
2. System resources (CPU/RAM) are constrained
3. Model needs optimization

**Solutions:**

#### 1. Use Faster Model (Recommended)
Edit your `.env` file to use a smaller, faster model:
```bash
OLLAMA_FAST_MODEL=phi3:mini     # Default, fastest
# or try:
OLLAMA_FAST_MODEL=phi3:3.8b     # Alternative
OLLAMA_FAST_MODEL=llama3.2:3b   # Even smaller
```

#### 2. Increase System Resources
- Close other applications to free up RAM
- Increase Docker memory if using containers
- Consider using a machine with better CPU

#### 3. Pull and Optimize Models
```bash
# Pull the fast model
ollama pull phi3:mini

# Test model performance
time ollama run phi3:mini "What is 2+2?"

# If slow, try smaller model
ollama pull phi3:3.8b
```

#### 4. Configure Gemini as Fallback
To have a reliable fallback, add your Gemini API key:

1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `.env`:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

#### 5. Check Ollama Service
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
# macOS: killall ollama && ollama serve
# Linux: sudo systemctl restart ollama
```

### Issue: "Gemini failed, using fallback"

**Causes:**
- No Gemini API key configured
- Invalid API key
- Network issues
- API quota exceeded

**Solutions:**

1. **Add Gemini API Key** (if you want fallback):
   ```bash
   # Get free key: https://makersuite.google.com/app/apikey
   GEMINI_API_KEY=your_key_here
   ```

2. **Or Accept Fallback Responses**:
   - Fallback responses still work, but are less detailed
   - Fix Ollama for better responses

### Issue: Slow Response Times

**Optimization Tips:**

1. **Reduce Token Generation**:
   - Fast queries use 200 tokens (edited in code)
   - Detailed queries use 400 tokens

2. **Use Smaller Context**:
   - Prompts are automatically trimmed
   - Keep user queries concise

3. **Optimize Ollama**:
   ```bash
   # Edit model settings
   ollama show phi3:mini
   
   # Adjust num_thread in code (already set to 4)
   ```

### Performance Benchmarks

Expected response times:
- **phi3:mini** (fast): 5-10 seconds
- **llama3.1:8b** (detailed): 15-30 seconds
- **Gemini** (fallback): 2-5 seconds
- **Basic fallback**: Instant

### Monitoring

Check logs for LLM performance:
```bash
tail -f logs/clarifi_ai.log | grep "LLM\|Ollama\|Gemini"
```

### System Requirements

**Minimum (phi3:mini only):**
- 4GB RAM
- 2 CPU cores
- 5GB disk space

**Recommended (phi3:mini + llama3.1:8b):**
- 8GB RAM
- 4 CPU cores
- 10GB disk space

### Quick Fix Summary

1. **Immediate fix**: Add Gemini API key for reliable fallback
2. **Long-term fix**: Use faster machine or smaller models
3. **Alternative**: Increase timeouts (already done: 30s/60s)

### Testing

Test your LLM setup:
```bash
cd backend
python3 test_ollama.py
```

### Support

If issues persist:
1. Check Ollama logs: `ollama logs`
2. Check system resources: `top` or `htop`
3. Test with minimal query: "Hello"
