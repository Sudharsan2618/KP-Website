from wagtail.search.backends.base import BaseSearchBackend


class NoopSearchBackend(BaseSearchBackend):
    """Import-time backend used to avoid per-row remote index refreshes."""
    def add(self, model_or_object, obj=None):
        return None

    def delete(self, model_or_object, obj=None):
        return None

    def search(self, query, model_or_queryset, **kwargs):
        return model_or_queryset.none() if hasattr(model_or_queryset, "none") else []

    def autocomplete(self, query, model_or_queryset, **kwargs):
        return self.search(query, model_or_queryset, **kwargs)
