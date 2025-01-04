def mapped_model_to_schema(model, schema):
    for field, value in model.dict(exclude_unset=True).items():
        setattr(schema, field, value)

    return schema
