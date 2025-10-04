publications_prompt = """
From the NASA Space Biology publication summary below, extract the following entities and relationships in the exact format described.

0. Never send an incomplete response. Never send any other explanations or extra text.

1. Identify the following **Entity Types** from the text. Each entity must include a unique alphanumeric `id`. You will refer to these IDs when defining relationships. Do not invent new entity types beyond the ones defined below. 

   Entity Types:
   - label:'Publication', id:string, title:string; summary:string
       // The `id` should be the lowercase title with no spaces, punctuation, or special characters.
       // The `summary` should concisely describe the publication content.
   - label:'Experiment', id:string, name:string; goal:string
       // The `id` should be in camelCase format.
       // The `goal` summarizes what the experiment is trying to achieve.
   - label:'Organism', id:string, name:string; type:string
       // Represents any organism or biological subject studied.
       // The `type` describes the category (e.g., plant, animal, bacteria).
   - label:'Technology', id:string, name:string
       // Represents any instrument, sensor, or technology used.
   - label:'Mission', id:string, name:string; platform:string
       // Represents a NASA mission or platform where the experiment took place.
       // `platform` specifies the experimental environment.
   - label:'ResearchTopic', id:string, name:string
       // Represents the scientific focus (e.g., Growth, Development, Reproduction, Immunity).

2. Define the following **Relationship Types** as triples of `head|RELATIONSHIP|tail`.
   Use the entities’ `id` properties to refer to them.

   Relationships should include:
   - publication|DESCRIBES_EXPERIMENT|experiment
   - experiment|STUDIES_ORGANISM|organism
   - experiment|USES_TECH|technology
   - experiment|PART_OF_MISSION|mission
   - experiment|FOCUSES_ON|researchtopic

3. The output must be valid JSON with the following structure:
{
    "entities": [
        {"label":"Publication","id":string,"title":string,"summary":string},
        {"label":"Experiment","id":string,"name":string,"goal":string},
        ...
    ],
    "relationships": [
        "publicationid|DESCRIBES_EXPERIMENT|experimentid",
        "experimentid|USES_TECH|technologyid"
    ]
}

NASA Space Biology Publication text:
$pub_text
"""
