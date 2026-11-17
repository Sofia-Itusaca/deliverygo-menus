import logging, os, time, uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, ASCENDING, UpdateOne
from pymongo.errors import PyMongoError
from pydantic import BaseModel, Field, ConfigDict

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO")); log=logging.getLogger("deliverygo.menus")
MONGO_URL=os.getenv("MONGODB_URL","mongodb://deliverygo:deliverygo_local@localhost:27017/deliverygo?authSource=admin")
client=MongoClient(MONGO_URL,serverSelectionTimeoutMS=2500); db=client[os.getenv("MONGODB_DATABASE","deliverygo")]; collection=db["menus"]
class Dish(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str; restaurante_id:str; nombre:str; descripcion:str; categoria:str; precio:float=Field(gt=0,le=1000); imagen_url:str; disponible:bool=True
    @classmethod
    def from_doc(cls,d): return cls(id=d["_id"],**{k:v for k,v in d.items() if k!="_id"})
def image(code):return f"https://images.unsplash.com/{code}?auto=format&fit=crop&w=900&q=80"
RESTAURANTS=[f"10000000-0000-4000-8000-{i:012d}" for i in range(1,7)]
def seed():
    grills=[("Pollo a la brasa 1/8","Porción de pollo a la brasa con papas y cremas.",23.9,"photo-1598103442097-8b74394b95c6"),("Pollo a la brasa 1/4","Cuarto de pollo dorado, papas crocantes y ensalada.",34.9,"photo-1626082927389-6cd097cdc6ec"),("Pollo a la brasa entero","Pollo entero con papas familiares y cremas de la casa.",89.9,"photo-1532550907401-a500c9a57435"),("Papas fritas","Porción de papas doradas para compartir.",12.0,"photo-1573080496219-bb080dd4f877")]
    chinese=[("Arroz chaufa","Arroz salteado al wok con huevo, cebolla china y sillao.",24.9,"photo-1512058564366-18510be2db19"),("Tallarín saltado","Tallarines al wok con verduras frescas y salsa oriental.",26.9,"photo-1569718212165-3a8278d5f624"),("Pollo tipakay","Pollo crocante con salsa tamarindo agridulce.",29.9,"photo-1603133872878-684f208fb84b"),("Combinado","Arroz chaufa y tallarín saltado en una sola porción.",31.9,"photo-1563245372-f21724e3856d")]
    docs=[]
    for idx,rid in enumerate(RESTAURANTS):
        for n,(name,desc,price,img) in enumerate(grills if idx<3 else chinese):
            docs.append({"_id":str(uuid.uuid5(uuid.NAMESPACE_URL,f"deliverygo:{rid}:{n}")),"restaurante_id":rid,"nombre":name,"descripcion":desc,"categoria":"Acompañamiento" if name=="Papas fritas" else ("Pollo a la brasa" if idx<3 else "Plato de fondo"),"precio":price+(idx*0.5),"imagen_url":image(img),"disponible":True})
    collection.bulk_write([UpdateOne({"_id":d["_id"]},{"$setOnInsert":d},upsert=True) for d in docs],ordered=False)
@asynccontextmanager
async def lifespan(app):
    for attempt in range(30):
        try:
            client.admin.command("ping");collection.create_index([("restaurante_id",ASCENDING)]);collection.create_index([("restaurante_id",ASCENDING),("_id",ASCENDING)],unique=True);seed();log.info("MongoDB ready; seeded menus");break
        except PyMongoError as exc:
            if attempt==29:raise
            log.warning("MongoDB unavailable, retrying: %s",exc);time.sleep(2)
    yield;client.close()
app=FastAPI(title="DeliveryGo Menu Service",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("FRONTEND_ORIGINS","http://localhost:5173").split(","),allow_methods=["GET"],allow_headers=["*"])
def valid_id(value):
    try:return str(uuid.UUID(value))
    except (ValueError,AttributeError):raise HTTPException(400,"Identificador inválido.")
@app.get("/health/live")
def live():return {"status":"healthy"}
@app.get("/health/ready")
def ready():
    try:client.admin.command("ping");return {"status":"ready"}
    except PyMongoError:raise HTTPException(503,"MongoDB no está disponible.")
@app.get("/api/v1/menus/{restaurante_id}",response_model=list[Dish])
def menu(restaurante_id:str):
    rid=valid_id(restaurante_id)
    try:return [Dish.from_doc(x) for x in collection.find({"restaurante_id":rid})]
    except PyMongoError:log.exception("Menu lookup failed");raise HTTPException(503,"No se pudo consultar el menú.")
@app.get("/api/v1/menus/{restaurante_id}/{producto_id}",response_model=Dish)
def dish(restaurante_id:str,producto_id:str):
    rid=valid_id(restaurante_id)
    try:doc=collection.find_one({"restaurante_id":rid,"_id":producto_id})
    except PyMongoError:log.exception("Dish lookup failed");raise HTTPException(503,"No se pudo consultar el plato.")
    if not doc:raise HTTPException(404,"Plato no encontrado.")
    return Dish.from_doc(doc)
