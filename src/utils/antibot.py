from fake_headers import Headers


def get_fake_random_headers(
    browser: str | None = None,
    os: str | None = None,
    random: bool = True,
):
    headers = Headers(
        browser=browser,  # type: ignore
        os=os,  # type: ignore
        headers=random,
    ).generate()
    return headers
