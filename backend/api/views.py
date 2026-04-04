from rest_framework.decorators import api_view
from rest_framework.response import Response
from firebase_admin import firestore
from .ai_service import analyze_video_intent

@api_view(['GET', 'POST'])
def create_master_asset(request):
    # If someone just visits the link in their browser (GET request)
    if request.method == 'GET':
        return Response({"message": "Send a POST request to this URL to save a video!"})

    # If the frontend is sending us data (POST request)
    if request.method == 'POST':
        # 1. Connect to our Firestore database
        db = firestore.client()

        # 2. Grab the title the frontend sent us (or use a default)
        video_title = request.data.get('title', 'Untitled Sports Clip')

        # 3. Create a new folder (document) in Firestore
        doc_ref = db.collection('master_assets').document()
        doc_ref.set({
            'title': video_title,
            'status': 'Uploaded to backend',
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        # 4. Give the frontend a success message and the new Document ID!
        return Response({
            "message": "Success! Video saved to Firebase.",
            "document_id": doc_ref.id
        })
    

@api_view(['GET'])
def get_all_assets(request):
    # 1. Connect to the database
    db = firestore.client()
    
    # 2. Point to our 'master_assets' folder
    assets_ref = db.collection('master_assets')
    
    # 3. Grab ALL the documents inside that folder
    docs = assets_ref.stream()
    
    # 4. Create an empty list to hold our formatted data
    all_videos = []
    
    # 5. Loop through the documents and add them to our list
    for doc in docs:
        video_data = doc.to_dict()
        video_data['id'] = doc.id # Save the Firebase ID too!
        all_videos.append(video_data)
        
    # 6. Hand the list back to the frontend!
    return Response({"videos": all_videos})


@api_view(['POST'])
def add_detection(request, master_id):
    # 1. Connect to the database
    db = firestore.client()
    
    # 2. Point to the specific Master Video, and open a sub-folder called 'detections'
    detections_ref = db.collection('master_assets').document(master_id).collection('detections')
    
    # 3. Grab the info about where it was stolen (e.g., "Twitter" or "YouTube")
    platform_name = request.data.get('platform', 'Unknown Website')
    
    # 4. Create the new document inside the sub-folder
    new_doc = detections_ref.document()
    new_doc.set({
        'platform': platform_name,
        'status': 'Pending AI Analysis', # Person 1 (AI) will change this later!
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    ai_decision = analyze_video_intent(platform_name)
    new_doc.update({
        'status': ai_decision
    })
    
    # 5. Tell the frontend it worked
    return Response({
        "message": f"Analysis complete! This video was flagged as: {ai_decision}",
        "detection_id": new_doc.id,
        "final_status": ai_decision
    })


@api_view(['GET'])
def get_graph_data(request, master_id):
    db = firestore.client()
    
    # 1. Get the Master Video info
    master_ref = db.collection('master_assets').document(master_id)
    master_doc = master_ref.get()
    
    if not master_doc.exists:
        return Response({"error": "Master video not found!"}, status=404)
        
    master_data = master_doc.to_dict()
    master_data['id'] = master_doc.id
    master_data['type'] = 'MASTER' # We tell the frontend this is the center node
    
    # 2. Get all the Stolen Videos (Detections)
    detections_ref = db.collection('master_assets').document(master_id).collection('detections')
    detections_docs = detections_ref.stream()
    
    all_detections = []
    for doc in detections_docs:
        det_data = doc.to_dict()
        det_data['id'] = doc.id
        det_data['type'] = 'DETECTION' # We tell the frontend these are the branches
        all_detections.append(det_data)
        
    # 3. Package it all together for the D3.js Graph!
    graph_package = {
        "master_node": master_data,
        "branch_nodes": all_detections
    }
    
    return Response(graph_package)