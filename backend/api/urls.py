from django.urls import path
from . import views

urlpatterns = [
    # 1. Upload a Master Video
    path('upload/', views.create_master_asset, name='upload_asset'),
    
    # 2. Get all Master Videos
    path('assets/', views.get_all_assets, name='get_assets'),
    
    # 3. Report a stolen video (Detection)
    path('assets/<str:master_id>/detect/', views.add_detection, name='add_detection'),

    # The final link for the Frontend Graph!
    path('assets/<str:master_id>/graph/', views.get_graph_data, name='get_graph_data'),
]