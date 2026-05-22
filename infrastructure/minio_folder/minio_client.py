# # app/main.py
# from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
# from fastapi.responses import StreamingResponse
# from fastapi.middleware.cors import CORSMiddleware
# import io
# from datetime import datetime
# import uuid
# import redis
# from PIL import Image

# app = FastAPI()

# # CORS per Flutter
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Redis
# #redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

# class MinioClient:
#     def __init__(self, cache_service, ):
#         self.cache_service = cache_service


#     # Funzione per ottimizzare l'immagine
#     def optimize_image(image_bytes: bytes, max_size: int = 800) -> bytes:
#         """Ridimensiona e ottimizza l'immagine"""
#         img = Image.open(io.BytesIO(image_bytes))
        
#         # Converti in RGB se necessario
#         if img.mode in ("RGBA", "P"):
#             img = img.convert("RGB")
        
#         # Ridimensiona mantenendo aspect ratio
#         img.thumbnail((max_size, max_size))
        
#         # Salva in formato JPEG con qualità ottimizzata
#         output = io.BytesIO()
#         img.save(output, format="JPEG", quality=85, optimize=True)
#         return output.getvalue()

# @app.post("/users/{user_id}/profile-picture")
# async def upload_profile_picture(
#     user_id: int,
#     file: UploadFile = File(...)
# ):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="File must be an image")
    
#     # Leggi il file
#     contents = await file.read()
    
#     # Ottimizza l'immagine
#     optimized_image = optimize_image(contents)
    
#     # Genera nome file univoco
#     file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
#     filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
    
#     # Upload su MinIO
#     MinioClient.put_object(
#         bucket_name=BUCKET_NAME,
#         object_name=filename,
#         data=io.BytesIO(optimized_image),
#         length=len(optimized_image),
#         content_type=file.content_type
#     )
    
#     # URL per l'immagine (usa un endpoint API o URL diretto)
#     picture_url = f"/api/users/{user_id}/profile-picture"
    
#     # Salva metadata nel DB (esempio con SQLAlchemy)
#     # db_user.profile_picture_url = picture_url
#     # db.commit()
    
#     # Invalida cache Redis
#     cache_key = f"user_profile:{user_id}"
#     cache_service.delete(cache_key)
    
#     return {"message": "Foto profilo aggiornata", "url": picture_url}

# @app.get("/users/{user_id}/profile-picture")
# async def get_profile_picture(user_id: int):
#     # Controlla cache Redis
#     cache_key = f"profile_picture:{user_id}"
#     cached_url = redis_client.get(cache_key)
    
#     if cached_url:
#         # Recupera dal DB l'URL o cerca l'ultima immagine nel bucket
#         # Per semplicità, assumiamo che l'immagine sia nominata con user_id
#         try:
#             # Lista oggetti nel bucket per questo user
#             objects = minio_client.list_objects(
#                 BUCKET_NAME,
#                 prefix=f"{user_id}/",
#                 recursive=True
#             )
            
#             # Prendi l'ultima immagine
#             latest_object = None
#             for obj in objects:
#                 latest_object = obj.object_name
            
#             if not latest_object:
#                 raise HTTPException(status_code=404, detail="Foto profilo non trovata")
            
#             # Recupera l'immagine da MinIO
#             response = minio_client.get_object(BUCKET_NAME, latest_object)
            
#             # Cache in Redis (1 ora)
#             redis_client.setex(cache_key, 3600, latest_object)
            
#             return StreamingResponse(
#                 response,
#                 media_type="image/jpeg",
#                 headers={"Cache-Control": "public, max-age=3600"}
#             )
            
#         except Exception as e:
#             raise HTTPException(status_code=404, detail="Foto non trovata")

# @app.delete("/users/{user_id}/profile-picture")
# async def delete_profile_picture(user_id: int):
#     try:
#         # Elimina tutte le immagini dell'utente
#         objects_to_delete = minio_client.list_objects(
#             BUCKET_NAME,
#             prefix=f"{user_id}/",
#             recursive=True
#         )
        
#         for obj in objects_to_delete:
#             minio_client.remove_object(BUCKET_NAME, obj.object_name)
        
#         # Aggiorna DB
#         # db_user.profile_picture_url = None
#         # db.commit()
        
#         # Invalida cache
#         redis_client.delete(f"user_profile:{user_id}")
#         redis_client.delete(f"profile_picture:{user_id}")
        
#         return {"message": "Foto profilo eliminata"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))