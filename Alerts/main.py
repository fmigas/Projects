"""
Main script.
"""

import warnings

warnings.filterwarnings("ignore")

import tools.functions as fn
import tools.prompts as prompts
from tools import Config
from sentence_transformers import SentenceTransformer
import os

config = Config()

# I used the simplest model from SentenceTransformers for speed and simplicity.
model = SentenceTransformer('all-MiniLM-L6-v2')
COLLECTION_NAME = 'alerts'


def main():
    # 0. Check if this is the first time the script is run. If yes, it will process a csv file and build a ChromaDB vectorestore.
    # check if a file 'companies.txt' exists in the 'files' folder; if not, run fn.initialization()
    if not os.path.isfile(config.files / 'companies.txt'):
        print("This is the first time you run this script. I need to do some preprocessing. It may take a while...")
        fn.initialization(collection_name = COLLECTION_NAME)

    while True:
        # 1. Get query from user
        query = input("Please enter your query. Type 'exit' to exit. Your query: ")

        if query == 'exit':
            print("Goodbye!")
            exit()

        print("Your query:", query)

        # 2. Get company name from query
        # For simplicity, we assume that the query refers to only one company. In real life, it may refer to multiple companies, of course.

        company_names = fn.get_company_names_for_query(query)

        # 3. Get metadata from query

        # With alert.csv file, we get some useful metadata, like company name, date, category or prioryt. I also added a 'region' field if it could be retrieved
        # from the company name.

        # We need to get all metadata from the user query so that we could use it in the ChromaDB query.

        print("Retrieving metadata from query...")
        metadata = fn.get_metadata_from_query(query = query, company = company_names.get('normalized_name'))

        # where_constructor() returns a string that can be used in a ChromaDB query
        where_metadata = fn.where_constructor(metadata, company_names)
        print(where_metadata)
        print('\n')

        # 4. Get query embedding

        query_embedding = model.encode([query])

        # 5. Retrieve top k=30 documents from ChromaDB using query embedding and metadata; texts are sorted by date which may add value or not, but definitely makes the results more interpretable

        n_results = 30  # it is a totally arbitrary value and could be optimized
        ff = fn.get_valid_texts(collection_name = COLLECTION_NAME, query_embedding = query_embedding, metadata = metadata, where_metadata = where_metadata,
                                n_results = n_results)

        # 6. Rerank top k documents using cohere rerank

        # I tested Cohere's rerank and it looked promising, but I did not have time to think about a smart way to integrate it into the pipeline.
        # There should be some kind of a threshold for the relevance score, but I did not have time to think about it.
        # ff = fn.get_reranked_documents(query = query, df = df)

        # 7. Final relevance check with LLM
        # If the query does not refer to any specific categories, we need to check if the retrieved texts are relevant to the query.
        # It is a costly step and it may take a while, but I tested it on some queries and my first impression was that it added value to the final result.

        if metadata.get('category').get('categories')[0] == 'none':
            print("Checking source texts relevance with LLM, it may take a while...")
            ff = fn.get_relevance_from_llm(df = ff, query = query)
            ff['relevance'] = ff['relevance'].apply(lambda x: x.lower())
            ff = ff[ff['relevance'] == 'yes']

        # 8. Send final query and valid texts to LLM and get response

        if ff.shape[0] == 0:
            print("No relevant documents found.")
            exit()
        else:
            valid_texts = ff.text.tolist()
            ids = ff.id.tolist()
            baseline_information = "\n".join(valid_texts)
            ids = [str(i) for i in ids]
            ids_used = ", ".join(ids)
            ids_used = f"IDs used: {ids_used}"
            print("Sending query to LLM...")
            first_reply = fn.get_reply_from_llm_LCEL(prompt_template = prompts.prompt_summary, args = {'query': query, 'baseline_information': baseline_information})

            print("Final reply:")
            fn.print_reply(first_reply, ids_used)
            print("\n")


if __name__ == '__main__':
    main()
