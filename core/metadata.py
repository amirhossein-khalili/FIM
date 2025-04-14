from rest_framework.metadata import SimpleMetadata


class CustomMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        # Get the default metadata
        metadata = super().determine_metadata(request, view)

        # Customize metadata
        metadata["name"] = view.get_view_name()
        # metadata["description"] = view.get_view_description()

        # Add custom information
        # metadata["custom_info"] = "This is a custom metadata field."

        # Include serializer information if available
        if hasattr(view, "get_serializer"):
            serializer = view.get_serializer()
            metadata["fields"] = self.get_serializer_info(serializer)

        # Add example responses if available
        if hasattr(view, "get_examples"):
            metadata["examples"] = view.get_examples()

        return metadata

    def get_serializer_info(self, serializer):
        """
        Return a dictionary representing serializer information.
        """
        serializer_info = super().get_serializer_info(serializer)
        # Custom processing of serializer fields if needed
        return serializer_info
