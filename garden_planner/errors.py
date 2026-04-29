"""User-friendly exception types for the garden planner app."""


class GardenPlannerError(Exception):
    """Base class for errors the UI can safely show to a user."""


class MissingApiKeyError(GardenPlannerError):
    """Raised when the Perenual API key is not configured."""


class LocationLookupError(GardenPlannerError):
    """Raised when Open-Meteo cannot resolve the entered location."""


class PlantLookupError(GardenPlannerError):
    """Raised when Perenual cannot find a matching plant."""


class ApiRequestError(GardenPlannerError):
    """Raised when a live API request fails or returns unexpected data."""


class InputValidationError(GardenPlannerError):
    """Raised when the user submits incomplete or invalid inputs."""

