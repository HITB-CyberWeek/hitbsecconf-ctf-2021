import { Body, Controller, Get, Path, Post, Route } from "tsoa";
import { knex } from "../app";

@Route("projects")
export class ProjectsController extends Controller {

    @Post()
    public async createProject(
        @Body() b: { name: string }
    ): Promise<void> {
        let p = await knex("projects")
            .returning("id")
            .insert({ "name": b.name })
            .onConflict("name")
            .merge();

        return p[0];
    }

    @Get("{projectId}")
    public async getProjectInfo(
        @Path() projectId: string,
    ): Promise<void> {
        let projects = await knex("projects").where({ "id": projectId }).select()
        if (projects.length == 0) {
            this.setStatus(404);
            return;
        }

        return projects[0];
    }

    @Post("{projectId}")
    public async putData(
        @Path() projectId: string,
        @Body() b: { k: string, v: string }
    ): Promise<void> {
        await knex("data")
            .insert({ "project_id": projectId, k: b.k, v: b.v })
            .onConflict(["project_id", "k"]).merge();
    }

    @Get("{projectId}/{k}")
    public async getData(
        @Path() projectId: string,
        @Path() k: string
    ): Promise<void> {
        let projects = await knex("projects").where({ "id": projectId }).select()
        if (projects.length == 0) {
            this.setStatus(404);
            return;
        }

        let project = projects[0];
        let table = project["active"] ? "data" : "archived_data";
        let res = await knex(table)
            .where({ "project_id": projectId, "k": k }).select("v");

        if (res.length == 0) {
            this.setStatus(404);
            return;
        }

        return res[0]["v"];
    }
}
