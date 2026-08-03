import importlib.util
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


class DummyFastAPI:
    def __init__(self, *args, **kwargs):
        pass

    def add_middleware(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def get(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


class DummyBaseModel:
    def __init__(self, *args, **kwargs):
        pass


class DummyPlainTextResponse(str):
    pass


class DummyStreamingResponse:
    def __init__(self, content, media_type):
        self.content = content
        self.media_type = media_type


fastapi_module = types.ModuleType("fastapi")
fastapi_module.FastAPI = DummyFastAPI
fastapi_module.Request = object
sys.modules["fastapi"] = fastapi_module

responses_module = types.ModuleType("fastapi.responses")
responses_module.PlainTextResponse = DummyPlainTextResponse
responses_module.StreamingResponse = DummyStreamingResponse
sys.modules["fastapi.responses"] = responses_module

middleware_module = types.ModuleType("fastapi.middleware")
sys.modules["fastapi.middleware"] = middleware_module

cors_module = types.ModuleType("fastapi.middleware.cors")
cors_module.CORSMiddleware = object
sys.modules["fastapi.middleware.cors"] = cors_module

pydantic_module = types.ModuleType("pydantic")
pydantic_module.BaseModel = DummyBaseModel
sys.modules["pydantic"] = pydantic_module

sys.modules["dotenv"] = types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None)
sys.modules["groq"] = types.SimpleNamespace(Groq=lambda *args, **kwargs: types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda *args, **kwargs: []))))
requests_module = types.ModuleType("requests")
requests_module.get = lambda *args, **kwargs: None
sys.modules["requests"] = requests_module

spec = importlib.util.spec_from_file_location("server.main", ROOT / "main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_refresh_knowledge_deduplicates_and_updates():
    module.KNOWLEDGE_STORE_PATH = ROOT / "test_knowledge_store.json"
    module.knowledge_store = {}

    existing = {"https://oticfoundation.org": {"title": "Old", "content": "old"}}
    new = {"https://oticfoundation.org": {"title": "New", "content": "fresh"}}

    module.persist_knowledge(existing, new)

    saved = module.load_knowledge_store()
    assert saved["https://oticfoundation.org"]["title"] == "New"
    assert saved["https://oticfoundation.org"]["content"] == "fresh"


def test_simple_greetings_use_brief_style():
    assert module.determine_response_style("hello") == "brief"
    assert module.determine_response_style("can you tell me about the company") == "detailed"
