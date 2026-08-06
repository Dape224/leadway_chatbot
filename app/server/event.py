import logging
import inngest



inngest_client = inngest.Inngest(
    app_id="my_fastapi_app",
    is_production= True, 
    logger=logging.getLogger("uvicorn"),
)

   