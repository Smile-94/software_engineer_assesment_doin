from pydantic import Field, model_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class AuthenticationSettings(PydanticBaseSettings):
    """
    Authentication settings loaded via Pydantic.
    """

    # Django password validator definitions (final structure expected by Django)
    AUTH_PASSWORD_VALIDATORS: list[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def build_auth_password_validators(self) -> "AuthenticationSettings":
        # Enforce a fixed, secure set of password validators
        # to avoid partial or unsafe configuration via environment variables
        self.AUTH_PASSWORD_VALIDATORS = [
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
            },
        ]
        return self


authentication_config = AuthenticationSettings()
