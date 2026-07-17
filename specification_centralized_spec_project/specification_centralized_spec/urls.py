import importlib
import os

urlpatterns = []

split_urls_dir = os.path.join(os.path.dirname(__file__),"split_urls")

for filename in os.listdir(split_urls_dir):
    if filename.endswith("_urls.py") and filename != "__init__.py":
        module_name = f"specification_centralized_spec.split_urls.{filename[:-3]}"
        module = importlib.import_module(module_name)
        if hasattr(module, "urlpatterns"):
            urlpatterns += module.urlpatterns