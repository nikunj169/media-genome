from google.cloud import aiplatform
from video_genome import video_to_vector

PROJECT_ID = "mediagenome-493416"
REGION = "us-central1"

ENDPOINT_RESOURCE_NAME = "projects/695416378766/locations/us-central1/indexEndpoints/7351820727449812992"
DEPLOYED_INDEX_ID = "mediagenome_deployed"

aiplatform.init(project=PROJECT_ID, location=REGION)

endpoint = aiplatform.MatchingEngineIndexEndpoint(
    ENDPOINT_RESOURCE_NAME
)

def search_video(video_path):
    vector = video_to_vector(video_path).tolist()

    response = endpoint.find_neighbors(
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[vector],
        num_neighbors=1,
    )

    neighbor = response[0][0]

    asset_id = neighbor.id
    similarity = 1 - neighbor.distance

    return asset_id, similarity


def classify_similarity(score):
    if score >= 0.75:
        return "MATCH"
    elif score >= 0.65:
        return "WEAK_MATCH"
    else:
        return "NO_MATCH"


if __name__ == "__main__":
    video_path = "videos/original.mp4"

    asset_id, score = search_video(video_path)

    print("Matched Asset:", asset_id)
    print("Similarity:", score)
    print("Classification:", classify_similarity(score))