from fastapi import FastAPI
from pydantic import BaseModel

from best_alliance_survirvors import AllianceCenterSurvivorOption, find_best_survivor_set_threshold
from shiny_servers import filter_shiny_servers

app = FastAPI()


class GetShinyServersPayload(BaseModel):
    data: list


class FindBestSurvivorSetThreshold(BaseModel):
    options: tuple[AllianceCenterSurvivorOption, AllianceCenterSurvivorOption]

@app.post("/shiny-servers")
def get_shiny_servers(item: GetShinyServersPayload):
    return {"message": filter_shiny_servers(item.data)}


@app.post("/best-survivor-set")
def best_survivor_set(item: FindBestSurvivorSetThreshold):
    return {"message": find_best_survivor_set_threshold(item.options)}


