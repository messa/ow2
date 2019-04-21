from pytest import mark


def test_import():
    import overwatch_hub


@mark.asyncio
async def test_db(db):
    pass


@mark.asyncio
async def test_model(model):
    assert await model.streams.list_all() == []
