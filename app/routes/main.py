from flask import Blueprint, render_template, request, jsonify
from app.services.api_services import get_biological_function, get_protein_interactions, fetch_diseases, fetch_variants
#from app.services.api_services import fetch_gnomad_population_data

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/api/biological-function", methods=["GET"])
def biological_function():
    gene = request.args.get("gene")
    if not gene:
        return jsonify({"error": "Gene name is required"}), 400
    return jsonify(get_biological_function(gene))

@main.route("/api/protein-interactions", methods=["GET"])
def protein_interactions():
    gene = request.args.get("gene")
    if not gene:
        return jsonify({"error": "Gene name is required"}), 400
    return jsonify({"interactions": get_protein_interactions(gene)})

@main.route('/api/diseases', methods=["GET"])
def get_diseases():
    gene = request.args.get('gene')
    if not gene:
        return jsonify({"error": "Gene name is required"}), 400
    
    # Fetch disease associations using the updated function
    disease_data = fetch_diseases(gene)
    return jsonify(disease_data)

@main.route("/api/variants", methods=["GET"])
def variants():
    gene = request.args.get("gene")
    if not gene:
        return jsonify({"error": "Gene symbol is required"}), 400
    
    # Call the fetch_variants function from api_services
    data = fetch_variants(gene)
    return jsonify(data)


from app.services.api_services import chatbot_response

@main.route("/api/chatbot", methods=["POST"])
def chatbot():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    bot_response = chatbot_response(user_message)
    return jsonify({"response": bot_response})
from flask import request, jsonify
from app.services.api_services import get_biological_function

@main.route('/api/chat', methods=['GET'])
def chat():
    message = request.args.get('message')
    if message:
        # Check if the message is asking for the biological function
        if "biological function" in message.lower():
            # Extract the gene name (assuming the format is like "TP53")
            gene = extract_gene_from_message(message)
            if gene:
                # Call the get_biological_function function to get the biological function
                bio_function = get_biological_function(gene)
                return jsonify({"reply": bio_function['function']})
            else:
                return jsonify({"reply": "Could not extract gene name from your question."})
        
        # For other cases, return a generic response or call a chatbot model
        reply = "I can provide biological function information. Ask about a gene!"
        return jsonify({"reply": reply})
    
    return jsonify({"reply": "Sorry, I didn't understand that."})

def extract_gene_from_message(message):
    # Simple heuristic to extract gene name from the message (e.g., TP53, BRCA1)
    # This is just an example; you can make this more sophisticated if needed
    words = message.split()
    for word in words:
        if word.isalpha() and len(word) > 1:
            return word  # Return the first gene-like word found
    return None

@main.route('/population-heatmap', methods=['GET'])
def population_heatmap():
    """
    Route to fetch population frequency data for a gene/variant and generate a heatmap.
    """
    gene = request.args.get('gene')  # Gene name, for now we assume it's directly passed
    variant_id = request.args.get('variant_id')  # Variant ID is passed directly
    
    # Fetch gnomAD population data
    if not variant_id:
        return jsonify({"error": "Variant ID is required."}), 400
    
    gnomad_data = fetch_gnomad_population_data(variant_id)
    
    if "error" in gnomad_data:
        return jsonify({"error": gnomad_data["error"]}), 400

    # Prepare the population data for the heatmap
    populations = ['AFR', 'AMR', 'EAS', 'SAS', 'EUR']  # Modify this as needed
    frequencies = [gnomad_data.get(pop, 0) for pop in populations]
    
    # Convert to DataFrame
    df = pd.DataFrame(frequencies, columns=['Frequency'], index=populations)

    # Generate the heatmap plot
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(df.T, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Frequency'}, ax=ax)
    ax.set_title(f'Population Frequencies for {variant_id}')
    ax.set_ylabel('Population')
    ax.set_xlabel('Variant')
    
    # Save the plot as a PNG image
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    
    # Convert image to base64 for embedding in HTML
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    return jsonify({"image": img_base64})
