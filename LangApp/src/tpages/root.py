import taipy.gui.builder as tgb


def creates_pages(pages):
    return [(f"/{page}", page.replace("_", " ").title()) for page in list(pages)[1:]]


with tgb.Page() as root:

    with tgb.part("header sticky"):
        with tgb.layout(
                # columns = "200px 12rem 1 8rem 150px",
                columns = "200px 80px 1",
                columns__mobile = "100px 50px 12rem 1 8rem",
                class_name = "header-content",
        ):
            tgb.text("Learn **with your text**", mode = "md", class_name = "logo_text")

            tgb.text("{user_name}", mode = "md", class_name = "user_name")

            with tgb.part("text-center"):
                tgb.navbar(
                    lov = "{creates_pages(pages)}",
                    inline = True,
                    class_name = "navbar",
                )

    with tgb.part("content"):
        tgb.html("br")

        tgb.content()
