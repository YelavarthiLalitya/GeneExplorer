import requests



def get_biological_function(gene):
    # Step 1: Search UniProt for human gene
    search_url = f"https://rest.uniprot.org/uniprotkb/search?query={gene}+AND+organism_id:9606&format=json&size=1"
    search_response = requests.get(search_url)
    search_data = search_response.json()


    if not search_data.get("results"):
        return {"error": "No data found or invalid gene name."}


    # Step 2: Get the first result
    entry = search_data["results"][0]
    accession = entry["primaryAccession"]


    # Step 3: Get function annotation
    entry_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    entry_response = requests.get(entry_url)
    entry_data = entry_response.json()


    function = "Not available"
    for comment in entry_data.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            function = comment.get("texts", [{}])[0].get("value", "")
            break


    # Step 4: Construct the UniProt structure URL directly (this is the link to the structure page)
    structure_url = f"https://www.uniprot.org/uniprotkb/{accession}/entry#structure"


    return {
        "function": function,
        "accession": accession,
        "structure_url": structure_url
    }


def resolve_string_id_to_name(string_id):
    """Resolve a STRING ID to a readable protein name."""
    url = "https://string-db.org/api/json/get_string_ids"
    params = {
        "identifiers": string_id,
        "species": 9606  # Human species (9606)
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data and "preferredName" in data[0]:
            return data[0]["preferredName"]
        return string_id  # fallback to STRING ID
    except Exception as e:
        print(f"Error resolving STRING ID {string_id}: {e}")
        return string_id  # return original ID if failed


def get_protein_interactions(gene):
    """Fetch protein-protein interactions from STRING database."""
    # Step 1: Query STRING for interactions
    url = "https://string-db.org/api/json/network"
    params = {
        "identifiers": gene,
        "species": 9606  # Human species (9606)
    }
   
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()


        # Step 2: Extract interaction data from STRING response
        interactions = []
        seen_proteins = set()  # Use a set to track unique interactions
        for item in response.json():
            partner_id = item.get("stringId_B") or item.get("stringId")
            score = item.get("score", 0)


            # Step 3: Resolve partner name from STRING ID
            partner_name = resolve_string_id_to_name(partner_id)


            # Check if interaction already exists
            if partner_name not in seen_proteins:
                seen_proteins.add(partner_name)  # Add to the set to track uniqueness
                interactions.append({
                    "name": partner_name,
                    "score": score
                })
       
        return interactions
    except requests.RequestException as e:
        print(f"Error fetching protein interactions for {gene}: {e}")
        return []


import time



DISGENET_API_URL = "https://www.disgenet.org/api/v1/gda/summary"
DISGENET_API_KEY = "YOUR API KEY"  # Replace this securely later



def get_uniprot_id(gene_symbol, retries=3):
    url = f"https://rest.uniprot.org/uniprotkb?query={gene_symbol}&format=tab&columns=id"
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.text.strip()
            if not data:
                return None
            lines = data.splitlines()
            if len(lines) > 1:
                return lines[1].split("\t")[0]
            else:
                return None
        except requests.exceptions.Timeout:
            print(f"Request timed out, retrying {attempt + 1}/{retries}...")
            attempt += 1
            time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    return None


def fetch_diseases(gene_symbol):
    # Get the UniProt ID for the gene symbol
    uniprot_id = get_uniprot_id(gene_symbol)
    
    if uniprot_id is None:
        return {"error": "Could not retrieve UniProt ID for gene"}
    
    # Query DisGeNET using the UniProt ID
    url = f"https://disgenet.com:443/api/v1/gda/summary?gene={uniprot_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response with disease data
    else:
        print(f"Error fetching diseases for {gene_symbol}: {response.status_code}")
        return {"error": "Error fetching diseases"}

import requests

# Function to fetch variant data for a given gene (ClinVar + gnomAD)
def fetch_variants(gene):
    clinvar_data = fetch_clinvar_data(gene)
    gnomad_data = fetch_gnomad_data(gene)
    
    return {
        'clinvar': clinvar_data,
        'gnomad': gnomad_data
    }

# Function to fetch ClinVar data
def fetch_clinvar_data(gene):
    url = f'https://api.ncbi.nlm.nih.gov/variation/v0/variant/clinvar/{gene}'  # Adjust URL as needed
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Returning the full ClinVar data
    else:
        return {'error': 'No ClinVar data available for this gene'}


from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained GPT-2 model for chatbot (can be loaded into memory once for efficiency)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

def chatbot_response(user_input):
    inputs = tokenizer.encode(user_input, return_tensors="pt")
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2, top_k=50, top_p=0.95)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response



def fetch_gnomad_population_data(variant_id):
    """
    Fetch population frequency data for a variant from gnomAD API.
    """
    url = f"https://gnomad.broadinstitute.org/api/variant/{variant_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Assuming the data has population frequencies
        data = response.json()
        population_frequencies = data.get("population_frequencies", {})
        
        return population_frequencies
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching gnomAD data for {variant_id}: {e}"}
