import inflect

# Create an inflect engine
p = inflect.engine()


def plural_to_singular_english(original_word):

    """
    Aktualnie działa tylko dla języka angielskiego.
    :param original_word:
    :return:
    """
    singular_word = p.singular_noun(original_word)
    return singular_word if singular_word else original_word


# plural_word = "conversations"
# singular_word = plural_to_singular(plural_word)
# print(f"The singular form of '{plural_word}' is '{singular_word}'.")
#

# plural_word = "men"
# singular_word = plural_to_singular_english(plural_word)
# print(f"The singular form of '{plural_word}' is '{singular_word}'.")


