"""Project-specific exceptions."""


class AvgfpAugmentationError(Exception):
    """Base exception for package errors."""


class MissingAssetError(AvgfpAugmentationError):
    """Raised when a required data asset is absent."""


class AssetCoverageError(AvgfpAugmentationError):
    """Raised when an optional asset exists but does not cover enough variants."""
