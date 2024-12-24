import requests
import re
import yaml
import pandas as pd

def find_patterns(text):
    """
    Finds all matches of the pattern ????-????-???? in the text.
    
    :param text: The input string to search.
    :return: A list of matched strings.
    """
    pattern = r">.{4}-.{4}-.{4}<"
    matches = re.findall(pattern, text)
    matches = [match.split('<')[0].split('>')[1] for match in matches]
    return matches

def make_request(url, params=None, headers=None):
    """
    Makes a GET request to the specified URL.
    
    :param url: The URL of the website to send the request to.
    :param params: Dictionary of query string parameters (optional).
    :param headers: Dictionary of request headers (optional).
    :return: Response object if the request is successful, None otherwise.
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

with open('config.yaml', 'r') as file:
    data = yaml.safe_load(file)

urls = data["config"]["urls"]

df = pd.read_csv(data["config"]["filename"])
df = df.dropna()
sku_dict = df.set_index('SKU ID')[['SKU description', 'Subtotal ($)']].apply(list, axis=1).to_dict()

# queries = df["SKU ID"].to_list()

storage = []
for url in urls:
    response = make_request(url).text
    matches = find_patterns(response)
    storage = storage + matches


ansT = {}
ansF = {}
for query in sku_dict.keys():
    if query in storage:
        ansT[query] = sku_dict[query]
    else:
        ansF[query] = sku_dict[query]

if data["config"]["mode"]:
    print("True:")
    for i, key in enumerate(ansT.keys()):
        print(f"\t{i} - {key}: {ansT[key]}")
    print(f"Total: {len(ansT)}")
else:
    print("False:")
    for i, key in enumerate(ansF.keys()):
        print(f"\t{i} - {key}: {ansF[key]}")
    print(f"Total: {len(ansF)}")
