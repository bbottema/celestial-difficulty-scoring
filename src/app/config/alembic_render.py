from app.orm.model.wavelength_type import WavelengthType


def render_item(type_, obj, autogen_context):
    """Tell Alembic how to render custom SQLAlchemy objects during autogenerate.

    Without this, Alembic may emit fully-qualified references (e.g.
    `app.orm.model...`) without adding the necessary imports to the migration,
    leading to runtime NameError when applying migrations.
    """

    if type_ == "type" and isinstance(obj, WavelengthType):
        autogen_context.imports.add(
            "from app.orm.model.wavelength_type import WavelengthType"
        )
        return "WavelengthType()"

    return False
