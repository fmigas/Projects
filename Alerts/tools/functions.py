"""
I decided to put all functions in one file for simplicity.
In real life, I would split them into separate files and folders for better readability and maintainability.

"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import chromadb
import cohere
from typing import Any

import tools.prompts as prompts

import textwrap
import re
import json
import pandas as pd
from tools import Config
import os

config = Config()


def get_categories():
    """
    It retrieves all categories from the alerts csv file and saves them to a txt file for further processing.
    :return:
    """
    df = pd.read_csv(config.files / 'alerts.csv')

    categories = df['Category'].unique().tolist()
    categories = "\n".join(categories)
    with open(config.files / 'categories.txt', 'w') as f:
        f.write(categories)


def get_reply_from_llm_LCEL(prompt_template: str, args: dict) -> str:
    """
    The main function that gets a reply from LLM.
    I used LangChain for this project, but it could be any other framework, like LlamaIndex, for example.

    Orignally, I wrote it as an async function, but I had some problems with OpenAI API and I decided to rewrite it as a sync function.
    For production, an async function probably would be a better choice.

    :param query: query
    :param prompt_template: template from a prompts.py file
    :return:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    variables = prompt.input_variables

    to_run = {variable: RunnablePassthrough() for variable in variables}

    output_parser = StrOutputParser()
    model = config.chat4
    chain = (
            to_run
            | prompt
            | model
            | output_parser
    )

    reply = chain.invoke(args)

    try:
        reply = json.loads(reply)
    except:
        pass

    return reply


def get_metadata_from_query(query: str, company: str) -> dict:
    """
    This function gets metadata from query.

    :param company: company name retrieved from the query
    :param query: query
    :return:
    """

    with open(config.files / 'categories.txt', 'r') as f:
        categories = f.read()

    metadata = {}

    # this 'company' metadata objective is to find out if a query refers only to a specific company, or to the broad market
    # if it refers to a specific company, we would use a company name in the ChromaDB query and filter out only alerts referring to this company
    # which reduces the risk of getting irrelevant alerts
    args = {"company": company, "query": query}
    metadata['market'] = get_reply_from_llm_LCEL(prompts.prompt_metadate_selection_market, args)
    print(metadata['market'])

    # I decided to take care of priority column in alerts.csv file only if the query refers to a high priority; otherwise, I would ignore it
    metadata['priority'] = get_reply_from_llm_LCEL(prompts.prompt_metadate_selection_priority, args)
    print(metadata['priority'])

    metadata['time'] = get_reply_from_llm_LCEL(prompts.prompt_metadate_selection_time, args)
    print(metadata['time'])

    # 'Region' metadata is retrieved from the company name and maybe it would make sense if a query refers to a specific country; I did not test it extensively
    metadata['region'] = get_reply_from_llm_LCEL(prompts.prompt_metadata_selection_region, args)
    print(metadata['region'])

    # All unique values from the 'Category' column in alerts.csv file are sent to LLM and the model is asked if the query refers to any of these categories
    # It may return multiple categories
    args = {"company": company, "query": query, "categories": categories}
    metadata['category'] = get_reply_from_llm_LCEL(prompts.prompt_metadate_selection_category, args)
    print(metadata['category'])

    return metadata


async def get_reply_from_llm_LCEL_async(prompt_template: str, args: dict) -> str:
    """
    I don't know why, but this function worked properly with OpenAI at first run, and then it stopped working.
    I decided to rewrite it as a sync function, but I left it here for future reference.

    :param query: query
    :param prompt_template: template z pliku docs_prompts.py
    :return:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    variables = prompt.input_variables

    to_run = {variable: RunnablePassthrough() for variable in variables}

    output_parser = StrOutputParser()
    model = config.chat3_5
    chain = (
            to_run
            | prompt
            | model
            | output_parser
    )

    reply = await chain.ainvoke(args)

    try:
        reply = json.loads(reply)
    except:
        pass

    return reply


async def get_metadata_from_query_async(query: str, company: str) -> dict:
    """
    Same as above.

    :param company:
    :param query: query
    :return:
    """

    with open(config.files / 'categories.txt', 'r') as f:
        categories = f.read()

    tasks = []
    args = {"company": company, "query": query}
    reply_market = await get_reply_from_llm_LCEL_async(prompts.prompt_metadate_selection_market, args)
    tasks.append(reply_market)

    reply_priority = await get_reply_from_llm_LCEL_async(prompts.prompt_metadate_selection_priority, args)
    tasks.append(reply_priority)

    reply_time = await get_reply_from_llm_LCEL_async(prompts.prompt_metadate_selection_time, args)
    tasks.append(reply_time)

    reply_region = await get_reply_from_llm_LCEL_async(prompts.prompt_metadata_selection_region, args)
    tasks.append(reply_region)

    args = {"company": company, "query": query, "categories": categories}
    reply_category = await get_reply_from_llm_LCEL_async(prompts.prompt_metadate_selection_category, args)
    tasks.append(reply_category)

    return tasks


def preprocess_company_names():
    """
    This function gets all unique company names and saves them to a txt file for further processing.
    :return:
    """
    df = pd.read_csv(config.files / 'alerts.csv')

    df['Company'] = df['Company'].str.lower()
    companies = df['Company'].unique().tolist()

    companies = [company.title() for company in companies]

    with open(config.files / 'companies.txt', 'w') as f:
        f.write('\n'.join(companies))


def normalize_company_names():
    """
    This function normalizes company names and saves them to a json file for further processing.
    By 'normalization' we understund getting the core name, region and other words from the company name.
    For example "Mondi Group Europe" is normalized to "Mondi", "Europe", ["Group"].

    :return:
    """
    with open(config.files / 'companies.txt', 'r') as f:
        companies = f.read()

    companies = companies.split('\n')

    normalized_names = {}
    for company in companies:
        company_decomposed = get_reply_from_llm_LCEL(prompt_template = prompts.prompt_company_names_normalization, args = {'company': company})
        normalized_names[company] = company_decomposed

    json.dump(normalized_names, open(config.files / 'normalized_company_names.json', 'w'))


def add_normalized_names_to_dataframe():
    """
    This function adds normalized company names to the alerts dataframe.
    In addtion, it saves normalized company names to a txt file for further usage.
    :return:
    """

    df = pd.read_csv(config.files / 'alerts.csv')

    normalized_names = json.load(open(config.files / 'normalized_company_names.json', 'r'))
    normalized_names = {k.lower(): v for k, v in normalized_names.items()}

    df['Company_normalized'] = df['Company'].apply(lambda x: normalized_names[x.lower()].get('core_name'))
    df['Region'] = df['Company'].apply(lambda x: normalized_names[x.lower()].get('region'))
    df['Region'] = df['Region'].apply(lambda x: x if x != 'Global' else None)
    df['Company'] = df['Company'].apply(lambda x: x.title())
    df.replace(to_replace = '', value = None, inplace = True)
    df.to_csv(config.files / 'alerts.csv')

    comp_normalized = df['Company_normalized'].unique().tolist()
    comp_normalized = "\n".join(comp_normalized)

    with open(config.files / 'companies_normalized.txt', 'w') as f:
        f.write(comp_normalized)

    return df


def get_company_names_for_query(query):
    """
    This function gets company names from the query.
    :param query: user query
    :return: a dictionary with full company name and normalized company name
    """
    query_lower = query.lower()

    with open(config.files / 'companies.txt', 'r') as f:
        companies = f.read()

    companies = companies.split('\n')

    with open(config.files / 'companies_normalized.txt', 'r') as f:
        companies_normalized = f.read()

    companies_normalized = companies_normalized.split('\n')

    comp_name = [company for company in companies if re.search(company.lower(), query_lower)]
    comp_normalized_name = [company for company in companies_normalized if re.search(company.lower(), query_lower)]

    names = {}
    if len(comp_name) == 0:
        names['name'] = ''  # in most scenarios, we would use None, but prompts are written in a way they work properly with empty string in case no company name is found
    else:
        names['name'] = comp_name[0]  # for simplicity we assume that the query never refers to more than one company; in real life it could not be true, of course

    if len(comp_normalized_name) == 0:
        names['normalized_name'] = ''
    else:
        names['normalized_name'] = comp_normalized_name[0]

    return names


def create_vectorestore(name: str) -> None:
    """
    Creates a collection in the vectorstore at the first app run.
    :return:
    """
    client = chromadb.PersistentClient(path = str(config.vectorestore))
    collection = client.create_collection(name = name)
    print("Created collection in vectorstore")


def add_alerts_to_vectorstore(df: pd.DataFrame, collection: Any) -> None:
    """
    This function adds alerts to the vectorstore.
    As an input, it takes a dataframe with alerts (not a single alert).
    I don't know if it would make more sense to add alerts one by one in production or in batches.

    I did not have time to analyze alerts themselves and check if they should be somewhat preprocessed / cleaned before adding to the vectorstore.
    Usually it is a good idea to do some preprocessing, get rid of noise, useless digressions etc. LLMs themselves are good at this.

    :param collection: ChromaDB collection
    :param df: dataframe with alerts and metadata in columns
    :return:
    """

    documents = df['Alert'].tolist()
    df['AlertId'] = df['AlertId'].apply(lambda x: str(x))
    ids = df['AlertId'].tolist()  # for simplicity we assume that AlertId is unique for each alert which of course is not a case if we would add another
    # dataframe with the same function; in real life we would use some other unique identifier, like a hash of the alert text

    metadatas = []
    for row in df.itertuples():
        temp = {}
        temp['date'] = getattr(row, 'Date')
        temp['priority'] = getattr(row, 'Priority')
        temp['category'] = getattr(row, 'Category')
        temp['company'] = getattr(row, 'Company')
        temp['company_normalized'] = getattr(row, 'Company_normalized')
        temp['region'] = getattr(row, 'Region')
        temp = {k: v for k, v in temp.items() if v is not None}
        metadatas.append(temp)

    collection.add(
        documents = documents,
        metadatas = metadatas,
        ids = ids,
    )

    print("Added alerts to vectorstore")


def get_collection(name: str) -> chromadb.Collection:
    """
    Returns collection handler.
    :return:
    """
    client = chromadb.PersistentClient(path = str(config.vectorestore))
    collection = client.get_collection(name = name)
    return collection


def initialization(collection_name: str):
    print("Preprocessing company names...")
    preprocess_company_names()
    print("Saving alerts categories to a file...")
    get_categories()

    # Some company names are simple, like 'Mondi', but some are more complex, like 'Mondi Group Europe'.
    # Some companies come from different regions, like 'Krones Germany' or 'Krones Spain'.
    # I decided to normalize company names to make it easier to use them ChromaDB queries.
    # Each company name is normalized to a core name, region and other words. Take a look at a prompt in tools/prompts.py for more details.

    print("Normalizing company names - it sends them to the LLM, it may take a while...")
    normalize_company_names()
    print("Adding normalized company names to the alerts csv file...")
    df = add_normalized_names_to_dataframe()

    # For this simple project I decided to use a locally run ChromaDB instance, just for simplicity and speed.
    # In a production-level solution, we would use a cloud-based ChromaDB instance or a different database like Pinecone etc.
    # For simplicity, I used the default sentence-transformers embedding model. For short texts, it is usually good enough.
    # For production, we would use something more advanced, like OpenAI embedding. I did not check if fine-tuning the embedding model would add value, of course.
    # In real-life scenario it could be tempting to verify (if we had time).

    # For simplicity, I accepted all default ChromaDB settings (e.g. tokenizer, distance metric etc.).
    # All valuves from columns 'Date', 'Priority', 'Category', 'Company', 'Company_normalized' are used as metadata.

    # Vectorestore is located in project/files folder.
    print("Building vectorestore...")
    create_vectorestore(name = collection_name)

    print("Adding alerts to the ChromaDB vectorestore - it may take a while...")
    collection = get_collection(name = collection_name)
    add_alerts_to_vectorstore(df = df, collection = collection)
    print("Initialization finished.")


def filter_texts_by_date(docs: dict, metadata: dict) -> tuple[list, list, list]:
    """
    This function filters texts by date if date is provided in the query.
    This function (like the majority of other functions in this script) DEFINITELY could be rewritten for better readability, maintainability and efficiency.

    :param docs: dictionary returned by ChromaDB query
    :param metadata: metadata retrieved from the user query
    :return: A list of texts filtered and sorted by date.
    """
    texts = docs.get("documents")[0]
    distances = docs.get("distances")[0]
    ids = docs.get("ids")[0]

    if 'start_date' in list(metadata['time'].keys()) and metadata['time']['start_date'] != 'none':
        start_date_query = metadata['time']['start_date']
        start_date_query = pd.to_datetime(start_date_query).strftime('%Y-%m-%d')
        start_date_query = pd.to_datetime(start_date_query)
    else:
        start_date_query = 'none'

    if 'stop_date' in list(metadata['time'].keys()) and metadata['time']['stop_date'] != 'none':
        stop_date_query = metadata['time']['stop_date']
        stop_date_query = pd.to_datetime(stop_date_query).strftime('%Y-%m-%d')
        stop_date_query = pd.to_datetime(stop_date_query)
    else:
        stop_date_query = 'none'

    valid_texts = []
    ids_ = []
    distances_ = []
    i = 0
    for text, id_, distance in zip(texts, ids, distances):
        date_alert = docs['metadatas'][0][i]['date']
        i += 1
        date_alert = pd.to_datetime(date_alert).strftime('%Y-%m-%d')
        date_alert = pd.to_datetime(date_alert)

        if start_date_query != 'none' and stop_date_query != 'none':
            if start_date_query <= date_alert <= stop_date_query:
                valid_texts.append(text)
                ids_.append(id_)
                distances_.append(distance)
        else:
            valid_texts.append(text)
            ids_.append(id_)
            distances_.append(distance)

    ids_ = list(map(int, ids_))

    df = pd.DataFrame({'text': valid_texts, 'id': ids_, 'distance': distances_})
    df.sort_values(by = 'id', inplace = True)

    return df


def where_constructor(metadata: dict, company_names: dict) -> dict:
    """
    This function takes a dictionary of filters and returns a dictionary that can be used as a filter in ChromaDB.
    :param company_names: company name retrieved from the user query
    :param metadata: metadata retrieved from the user query
    :return: A dictionary that can be used as a filter in ChromaDB.
    """

    where_metadata = {}
    if metadata.get('category').get('categories') != ['none']:
        where_metadata['category'] = metadata.get('category').get('categories')
        if len(where_metadata['category']) > 0:
            where_metadata['category'] = {"$in": where_metadata['category']}

    if metadata.get('market').get('market') == 'no':
        if company_names.get('normalized_name') is not None:
            where_metadata['company_normalized'] = company_names.get('normalized_name')

    if metadata.get('region').get('region') != 'none':
        where_metadata['region'] = metadata.get('region').get('region')

    if metadata.get('priority').get('priority') == 'High':
        where_metadata['priority'] = 'High'

    if len(where_metadata) == 1:
        return where_metadata
    elif len(where_metadata) > 1:
        where_metadata = [{k: v} for k, v in where_metadata.items()]
        where_metadata = {"$and": [where_metadata][0]}
        inner_data = where_metadata.get("$and")

        new_inner_data = []
        for val in inner_data:
            if isinstance(list(val.values())[0], list):
                new_inner_data.append({list(val.keys())[0]: {"$in": list(val.values())[0]}})
            else:
                new_inner_data.append(val)

        where_metadata = {"$and": new_inner_data}

        return where_metadata
    else:
        return None


def get_valid_texts(collection_name: str, query_embedding: list, metadata: dict, where_metadata: dict, n_results: int = 30) -> pd.DataFrame:
    """
    This function retrieves top k documents from ChromaDB using query embedding and metadata.

    :param collection_name: name of the collection in ChromaDB
    :param query_embedding: embedding of the query
    :param metadata: metadata retrieved from query
    :param where_metadata: metadata in a format that can be used as a filter in ChromaDB
    :param n_results: number of results to retrieve
    :return: A list of valid texts sorted by date.
    """
    collection = get_collection(name = collection_name)
    docs = collection.query(
        query_embeddings = query_embedding,
        n_results = n_results,
        where = where_metadata,
    )

    df = filter_texts_by_date(docs, metadata)
    return df


def print_reply(reply: str, ids: str) -> None:
    """
    It prints the reply from LLM and IDs of the documents used in the reply in a readable format with pagination.
    :param reply:
    :param ids:
    :return:
    """
    reply_lines = reply.split('\n')
    for line in reply_lines:
        wrapped_line = textwrap.fill(line, width = 80)
        print(wrapped_line)

    print('\n')

    ids_lines = ids.split('\n')
    for line in ids_lines:
        wrapped_line = textwrap.fill(line, width = 80)
        print(wrapped_line)
    print('\n')


def get_reranked_documents(query, df):
    """
    This function reranks documents using Cohere's rerank.
    I tested it a while but did not have a good idea how to integrate it into the pipeline.
    I decided to leave it here for future reference.

    :param query:
    :param df:
    :return:
    """

    cohere_key = os.getenv("COHERE_API_KEY")
    if cohere_key is None:
        print("Did not find COHERE_API_KEY in .env file. Cohere rerant step will be ignored.")
        return None

    co = cohere.Client(cohere_key)

    docs = df['text'].tolist()

    results = co.rerank(query = query, documents = docs, top_n = None, model = 'rerank-english-v2.0')
    results = results.results

    ff = pd.DataFrame()
    ff['score'] = [r.relevance_score for r in results]
    ff['text'] = [r.document.get('text') for r in results]
    merged_df = pd.merge(df, ff, on = 'text', how = 'inner')
    # df = pd.DataFrame({'text': [r.document.get('text') for r in re], 'score': [r.relevance_score for r in re]})
    return merged_df


def get_relevance_from_llm(df, query):
    """
    This function sends each text retrieved from a ChromaDB vectorstore to LLM and checks if it is relevant to the user query.
    It's a costly step, but in some scenarios I found it was the only way to get relevant results.
    For example for a query "Summarize Elopak CEO activity." both ChromaDB and Cohere's Rerank failed to separate relevant texts (directly referring to the CEO)
    from irrelevant texts (referring to the Elopak company in general).
    Or at least I could not find less costly way to do it.

    This function is used where there are not 'category' metadata found in the user query.

    :param df:
    :param query:
    :return:
    """

    texts = df.text.tolist()
    replies = []
    for text in texts:
        first_reply = get_reply_from_llm_LCEL(prompt_template = prompts.prompt_relevance, args = {'query': query, 'text': text})
        replies.append(first_reply)

    df['relevance'] = replies
    return df
