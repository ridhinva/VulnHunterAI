async def llm_complete(messages, model="openrouter/owl-alpha", api_key="", base_url="https://openrouter.ai/api/v1"):
    try:
        import litellm
        r = litellm.completion(model=model, messages=messages, api_key=api_key or None, api_base=base_url)
        return {"content": r.choices[0].message.content}
    except Exception as e: return {"error": str(e)}
