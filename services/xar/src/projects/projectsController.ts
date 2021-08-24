import { Body, Controller, Get, Path, Post, Route } from "tsoa";
import { knex } from "../app";

@Route()
export class IndexController extends Controller {
    @Get()
    public async index(): Promise<void> {
        this.setHeader("Location", "/docs");
        this.setStatus(302);
    }
}
@Route("projects")
export class ProjectsController extends Controller {

    /**
     * Create project
     *
     * @param b "Info about newly project"
     * @example b {
     *  "name": "super_project"
     * }
     */
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

    /**
     * Get info about project by projectId
     *
     * @param projectId "ProjectID returned from create method"
     * @pattern projectId [0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}
     * @example projectId "fe1bb302-78ce-40a9-9d17-3e3db7fee6fb"
     */
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

    /**
     * Put data to project
     *
     * @param projectId "ProjectID returned from create method"
     * @pattern projectId [0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}
     * @example projectId "fe1bb302-78ce-40a9-9d17-3e3db7fee6fb"
     * @param b "key and value info"
     * @example b {
     *   "k": "key1",
     *   "v": "some text data"
     * }
     */
    @Post("{projectId}")
    public async putData(
        @Path() projectId: string,
        @Body() b: { k: string, v: string }
    ): Promise<void> {
        await knex("data")
            .insert({ "project_id": projectId, k: b.k, v: b.v })
            .onConflict(["project_id", "k"]).merge();
    }

    /**
     * Get project's data
     *
     * @param projectId "ProjectID returned from create method"
     * @pattern projectId [0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}
     * @example projectId "fe1bb302-78ce-40a9-9d17-3e3db7fee6fb"
     * @param k "key"
     * @example k "key1"
     */
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
