import { writable } from "svelte/store";
import { Vec2 } from "./utils";

export interface App {
    mapSize: Vec2;
    physicalSize: Vec2;
}

export const app = writable<App>({
    mapSize: new Vec2(256, 256),
    physicalSize: new Vec2(2.0, 2.0),
});
